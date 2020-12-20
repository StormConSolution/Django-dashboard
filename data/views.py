import datetime
import json
from urllib.parse import urlsplit, parse_qs

from django import template
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import requests

from data import models as data_models
from data import charts

LOGIN_URL = '/login/'

ASPECT_COLORS = [
    'Pink', 'Crimson', 'Coral', 'Chocolate', 'DarkCyan', 'LightCoral', 'DarkOliveGreen',
    'LightSkyBlue', 'MintCream', 'PowderBlue', 'SandyBrown', 'Tomato', 'SeaGreen',
]

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

    context = {
        'project': this_project,
        'chart_data': get_chart_data(this_project, start, end, entity_filter, aspect_topic, aspect_name, lang_filter, source_filter),
        'query_string': request.GET.urlencode(),
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

    for i in range(len(context['aspects_total_data'])):
        context['aspects_total_data'][i]['width'] = (
            context['aspects_total_data'][i][
                'total_data'] / total_sum) * 100
    
    if chart_data.get('sentiment_f_data', []):
        context['total_data'] = sum(chart_data['sentiment_f_data'])
        context['total_positive'] = chart_data['sentiment_f_data'][0]
        context['total_negative'] = chart_data['sentiment_f_data'][1]

    return render(request, "project_new.html", context)


def top_entities(request, project_id):
    """
    Show the frequency of occurence for the entities for this data set.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    start = request.GET.get('start')
    end = request.GET.get('end')

    table = charts.TopEntityTable(
        this_project, start, end, request.GET.get(
            'entity'), request.GET.get('aspecttopic'),
        request.GET.get('aspectname'), request.GET.getlist(
            'filter_language'), request.GET.getlist('filter_source'),
    )

    return JsonResponse(table.render_data())


def entities(request, project_id):
    """
    Show the frequency of occurence for the entities for this data set.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    start = request.GET.get('start')
    end = request.GET.get('end')

    table = charts.EntityTable(
        this_project, start, end, request.GET.get('entity'), 
        request.GET.get('aspecttopic'),
        request.GET.get('aspectname'),
        request.GET.getlist('filter_language'),
        request.GET.getlist('filter_source'),
    )
    return JsonResponse(table.render_data())


def keywords(request, project_id):
    """
    Show the frequency of occurence for the keywords for this data set.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    start = request.GET.get('start')
    end = request.GET.get('end')

    table = charts.KeywordsTable(
        this_project, start, end, request.GET.get('entity'),
        request.GET.get('aspecttopic'), 
        request.GET.get('aspectname'), 
        request.GET.getlist('filter_language'),
        request.GET.getlist('filter_source'),
    )
    return JsonResponse(table.render_data())


def countries(request, project_id):
    """
    Show the total postive and negative sentiment for the countries for this data set.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    start = request.GET.get('start')
    end = request.GET.get('end')

    table = charts.CountriesTable(
        this_project, start, end, request.GET.get('entity'), 
        request.GET.get('aspecttopic'), 
        request.GET.get('aspectname'), 
        request.GET.getlist('filter_language'), 
        request.GET.getlist('filter_source'),
    )
    
    return JsonResponse(table.render_data())

def data_entries(request, project_id):
    """
    list all data entries for this project.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    start = request.GET.get('start')
    end = request.GET.get('end')

    table = charts.DataEntryTable(
        this_project,
        start,
        end,
        request.GET.get('entity'),
        request.GET.get('aspecttopic'),
        request.GET.get('aspectname'),
        request.GET.getlist('filter_language'),
        request.GET.getlist('filter_source'),
    )
    
    return JsonResponse(table.render_data())


def aspect_topics(request, project_id):
    """
    Show the frequency of occurence for the topics found in the aspects.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    start = request.GET.get('start')
    end = request.GET.get('end')

    table = charts.AspectTopicTable(
        this_project, start, end, request.GET.get('entity'),
        request.GET.get('aspecttopic'), 
        request.GET.get('aspectname'), 
        request.GET.getlist('filter_language'), 
        request.GET.getlist('filter_source'),
    )

    return JsonResponse(table.render_data())


def aspect_name(request, project_id):
    """
    Show the frequency of occurence of the topics related to the given aspect.
    """
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    start = request.GET.get('start')
    end = request.GET.get('end')

    table = charts.AspectNameTable(
        this_project, start, end, request.GET.get('entity'),
        request.GET.get('aspecttopic'),
        request.GET.get('aspectname'),
        request.GET.getlist('filter_language'),
        request.GET.getlist('filter_source'),
    )

    return JsonResponse(table.render_data())


@csrf_exempt
def create_project(request):
    """
    API endpoint for creating a project. May need some work as we go.

    `project_name`: the name of the Project. If it doesn't exist, create it.
    `username`: the user name to add to this project. User is assumed to exist.
    `aspect_model`: the aspect model this project will use.
    """
    if 'name' not in request.POST or 'username' not in request.POST:
        return JsonResponse({"status": "Fail", "description": "Both `name` and `username` are required"})

    proj, _ = data_models.Project.objects.get_or_create(
        name=request.POST['name'])

    if 'aspect_model' in request.POST:
        m, _ = data_models.AspectModel.objects.get_or_create(label=request.POST['aspect_model'])
        proj.aspect_model = m
        proj.save()

    user, _ = User.objects.get_or_create(username=request.POST['username'])
    proj.users.add(user)

    return JsonResponse({"status": "OK", "project_id": proj.id})

@csrf_exempt
def add_data(request, project_id):
    """
    Temporary API endpoint for loading data. May need some work as we go.
    Required: 
    source: where did the text come from, create if doesn't exist
    text: the text itself
    lang: language of the text
    with_entities=0/1: should we extract entities
    aspect_model: which aspect model, if any, to use
    date: date this item was created, defaults today
    """
    import time
    text = request.POST['text']
    lang = request.POST.get('lang', 'en')
    
    try:
        resp = requests.post('{HOST}/v4/{APIKEY}/score.json'.format(
            HOST=settings.API_HOST, APIKEY=settings.APIKEY), data={'text': text, 'lang': lang}).json()
        if 'score' in resp:
            sentiment = resp['score']
        else:
            return JsonResponse(resp)
    except Exception as e:
        return JsonResponse({"status": "FAIL", "message": "Could not add text = {} lang = {} because: {}".format(text, lang, e)})

    source, _ = data_models.Source.objects.get_or_create(
        label=request.POST['source'])
    
    project = data_models.Project.objects.get(pk=project_id)

    data = data_models.Data.objects.create(
        date_created=request.POST.get('date', datetime.datetime.now().date()),
        project=project,
        source=source,
        text=text,
        sentiment=sentiment,
        language=lang,
    )
    found_entities = []

    entities = {}
    if request.POST.get('with_entities'):
        entities = requests.post('{HOST}/v4/{APIKEY}/entities.json'.format(
            HOST=settings.API_HOST, APIKEY=settings.APIKEY), {'text': text, 'lang': lang}).json()

    for ent in entities.get('entities', []):
        entity_instance, created = data_models.Entity.objects.get_or_create(
            label=ent['title']
        )

        for clas in ent['classifications']:
            c_instance, created = data_models.Classification.objects.get_or_create(
                label=clas
            )
            entity_instance.classifications.add(c_instance)

        data.entities.add(entity_instance)

    if project.aspect_model:
        aspects = requests.post('{HOST}/v4/{APIKEY}/aspect.json'.format(
            HOST=settings.API_HOST, APIKEY=settings.APIKEY),
            {'text': text, 'neutral': 1, 'lang': lang, 'model': project.aspect_model.label}).json()

        for key, value in aspects.items():
            if key != "status" and aspects['status'] == 'OK':
                for v in value:
                    data_models.Aspect.objects.create(
                        data=data,
                        label=key,
                        chunk=v['chunk'],
                        sentiment=v['score'],
                        topic=v['sentiment_topic'],
                        sentiment_text=v['sentiment_text']
                    )
    
    # Add keywords.
    resp = requests.post('{HOST}/v4/{APIKEY}/keywords.json'.format(
        HOST=settings.API_HOST, APIKEY=settings.APIKEY), {'text':text, 'lang':lang}).json()

    print(resp)
    
    for keyword, count in resp.get('keywords', {}).items():
        kw, _ = data_models.Keyword.objects.get_or_create(label=keyword)
        for i in range(count):
            data.keywords.add(kw)

    return JsonResponse({"status": "OK"})


def export_card(request):
    pass
