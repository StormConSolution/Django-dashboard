import collections
import datetime
import json
import time

from django import template
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q, F
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.urls import reverse

from data import models as data_models
from data import charts

LOGIN_URL = '/login/'

MAX_TEXT_LENGTH = 30

ASPECT_COLORS = [
    'Pink', 'Crimson', 'Coral', 'Chocolate', 'DarkCyan', 'LightCoral', 'DarkOliveGreen',
    'LightSkyBlue', 'MintCream', 'PowderBlue', 'SandyBrown', 'Tomato', 'SeaGreen',
]

def collect_args(this_project, request):
    entity_filter = request.GET.get('entity')
    aspect_topic = request.GET.get('aspecttopic')
    aspect_name = request.GET.get('aspectname')

    # getting list of query params
    lang = request.GET.getlist('filter_language')
    src = request.GET.getlist('filter_source')
    # cleaning up the query params
    if lang:
        lang_filter = lang[0].split(",")
    else:
        lang_filter = lang
    if src:
        source_filter = src[0].split(",")
    else:
        source_filter = src

    if this_project.data_set.count() > 0:
        end = this_project.data_set.latest().date_created
    else:
        end = datetime.date.today()
    start = end - datetime.timedelta(days=30)

    if 'start' in request.GET and 'end' in request.GET:
        start = datetime.datetime.strptime(
            request.GET.get('start'), "%Y-%m-%d")
        end = datetime.datetime.strptime(request.GET.get('end'), "%Y-%m-%d")
    
    return dict(
        project=this_project,
        entity_filter=entity_filter,
        aspect_topic=aspect_topic,
        aspect_name=aspect_name,
        lang_filter=lang_filter,
        source_filter=source_filter,
        start=start,
        end=end
    )

def default_encoder(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


@login_required(login_url=LOGIN_URL)
def index(request):
    """
    The home page renders the latest project by default.
    """
    proj = data_models.Project.objects.filter(users=request.user)
    if proj:
        proj = proj.latest()
        return redirect(reverse('projects', kwargs={'project_id': proj.id}))
    else:
        # return forbiden if no projects, so that there is no crash
        return HttpResponseForbidden()


@login_required(login_url=LOGIN_URL)
def pages(request):
    context = {}

    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        load_template = request.path.split('/')[-1]
        html_template = loader.get_template(load_template)
        return HttpResponse(html_template.render(context, request))
    except template.TemplateDoesNotExist:
        html_template = loader.get_template('page-404.html')
        return HttpResponse(html_template.render(context, request))
    except:
        html_template = loader.get_template('page-500.html')
        return HttpResponse(html_template.render(context, request))


def get_chart_data(this_project, start, end, entity_filter, aspect_topic, aspect_name, lang_filter, source_filter):
    result = {
        "status": "OK",
        "colors": charts.COLORS["contrasts"],
    }

    for chart in data_models.ChartType.objects.all():
        if chart.load_async:
            continue
        instance = charts.CHART_LOOKUP[chart.label](
            this_project, start, end, entity_filter, aspect_topic, aspect_name, lang_filter, source_filter)
        data = instance.render_data()
        for key, value in data.items():
            result[key] = value
    
    return json.dumps(result, sort_keys=True, default=default_encoder)


@login_required(login_url=LOGIN_URL)
def projects(request, project_id):
    
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseRedirect(LOGIN_URL)

    entity_filter = request.GET.get('entity')
    aspect_topic = request.GET.get('aspecttopic')
    aspect_name = request.GET.get('aspectname')

    # getting list of query params
    lang = request.GET.getlist('filter_language')
    src = request.GET.getlist('filter_source')
    # cleaning up the query params
    if lang:
        lang_filter = lang[0].split(",")
    else:
        lang_filter = lang
    if src:
        source_filter = src[0].split(",")
    else:
        source_filter = src

    if this_project.data_set.count() > 0:
        end = this_project.data_set.latest().date_created
    else:
        end = datetime.date.today()
    start = end - datetime.timedelta(days=30)

    if 'start' in request.GET and 'end' in request.GET:
        start = datetime.datetime.strptime(
            request.GET.get('start'), "%Y-%m-%d")
        end = datetime.datetime.strptime(request.GET.get('end'), "%Y-%m-%d")

    chart_data = get_chart_data(
        this_project,
        start,
        end,
        entity_filter,
        aspect_topic,
        aspect_name,
        lang_filter,
        source_filter,
    )
    
    # Give them a link to see all results.
    latest = this_project.data_set.latest()
    earliest = this_project.data_set.earliest()

    view_all_link = '{}?start={}&end={}'.format(
        reverse('projects', kwargs={'project_id':project_id}),
        earliest.date_created.strftime('%Y-%m-%d'),
        latest.date_created.strftime('%Y-%m-%d')
    )

    context = {
        'project': this_project,
        'total':this_project.data_set.count(),
        'chart_data': chart_data,
        'query_string': request.GET.urlencode(),
        'view_all_link':view_all_link,
        'start_date': start,
        'end_date': end,
        'sources': data_models.Source.objects.filter(data__project=this_project).distinct()
    }

    # list of languages in a given project
    lan_data = list(data_models.Data.objects.filter(
        project=this_project).values('language').distinct())
    lang_list = []
    for lan in lan_data:
        lang_list.append(lan['language'])
    context['lang_list'] = lang_list
    context['languages'] = data_models.LANGUAGES
    # List of projects for the sidebar
    context['project_list'] = list(
        data_models.Project.objects.filter(users=request.user).values())
    context['aspects_total_data'] = []
    chart_data = json.loads(context['chart_data'])
    total_sum = 0
    color_index = 0

    for aspect in chart_data.get('aspect_t_labels', []):
        aspect_data = dict()
        
        aspect_data['name'] = aspect
        aspect_data['total_data'] = sum(
            item['label__count'] for item in chart_data['aspects'][aspect])
        aspect_data['color'] = ASPECT_COLORS[color_index]

        if color_index == len(ASPECT_COLORS) - 1:
            color_index = 0
        total_sum += aspect_data['total_data']
        color_index += 1
        context['aspects_total_data'].append(aspect_data)

    for i in range(len(chart_data.get('aspect_t_labels', []))):
        positive_data = chart_data['aspect_s_data'][0]['data'][i]
        negative_data = chart_data['aspect_s_data'][1]['data'][i]
        context['aspects_total_data'][i]['net_data'] = positive_data - negative_data
    
    # Compute the relative width for each aspect bar.
    for i in range(len(context['aspects_total_data'])):
        context['aspects_total_data'][i]['width'] = (
            context['aspects_total_data'][i][
                'total_data'] / total_sum) * 100
    
    if chart_data.get('sentiment_f_data', []):
        context['total_data'] = sum(chart_data['sentiment_f_data'])
        context['total_positive'] = chart_data['sentiment_f_data'][0]
        context['total_negative'] = chart_data['sentiment_f_data'][1]

    return render(request, "project.html", context)


def entities(request, project_id):
    """
    Show the frequency of occurence for the entities for this data set.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    args = collect_args(this_project, request)

    table = charts.EntityTable(**args)
    
    return JsonResponse(table.render_data())


def data_entries(request, project_id):
    """
    list all data entries for this project.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()
    
    args = collect_args(this_project, request)
    
    table = charts.DataEntryTable(**args)
    
    return JsonResponse(table.render_data())


def aspect_topics(request, project_id):
    """
    Show the frequency of occurence for the topics found in the aspects.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    args = collect_args(this_project, request)
    
    table = charts.AspectTopicTable(**args)

    return JsonResponse(table.render_data())


def aspect_name(request, project_id):
    """
    Show the frequency of occurence of the topics related to the given aspect.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    args = collect_args(this_project, request)

    table = charts.AspectNameTable(**args)

    return JsonResponse(table.render_data())

def aspect_topic_detail(request, project_id):
    """
    Renders sentiment text for topic specified.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)

    topic = request.GET.get('topic')

    aspects = data_models.Aspect.objects.filter(
        data__project=this_project,
        topic=topic
    )

    if int(request.GET.get('sentiment')) > 0:
        aspects = aspects.filter(sentiment__gt=0)
    else:
        aspects = aspects.filter(sentiment__lt=0)

    data = []
    for a in aspects.values('sentiment_text', 'chunk'):
        for t in a['sentiment_text']:
            if t != topic:
                data.append([
                    t, a['chunk']
                ])
    
    return JsonResponse({"data":data})

def aspect_topic_summary(request, project_id):
    """
    Renders sentiment text stats for topic specified.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)

    topic = request.GET.get('topic')

    aspects = data_models.Aspect.objects.filter(
        data__project=this_project,
        topic=topic
    )

    if int(request.GET.get('sentiment')) > 0:
        aspects = aspects.filter(sentiment__gt=0)
    else:
        aspects = aspects.filter(sentiment__lt=0)
    
    data = collections.defaultdict(int)
    for a in aspects.values('sentiment_text'):
        for t in a['sentiment_text']:
            if t != topic:
                data[t] += 1
    
    return JsonResponse({"data":list(data.items())})
