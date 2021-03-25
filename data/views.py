import collections
import datetime
import json
import time

from django import template
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, F, Sum, Case, When, Value, IntegerField
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.urls import reverse
from django.core import serializers
from django.forms.models import model_to_dict
from data import models as data_models
from data import charts
from django.db.models.functions import Coalesce
LOGIN_URL = '/login/'

MAX_TEXT_LENGTH = 30

ASPECT_COLORS = [
    'Pink', 'Crimson', 'Coral', 'Chocolate', 'DarkCyan', 'LightCoral',
    'DarkOliveGreen', 'LightSkyBlue', 'MintCream', 'PowderBlue', 'SandyBrown',
    'Tomato', 'SeaGreen', 'DarkKhaki', 'DarkOrange', 'DarkSlateGray',
    'DeepSkyBlue', 'DimGrey', 'DarkRed', 'Gold', 'IndianRed', 'Lavender',
    'LightGrat', 'LightSlateGray',
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

    if 'from' in request.GET and 'to' in request.GET:
        start = datetime.datetime.strptime(request.GET.get('from'), "%Y-%m-%d")
        end = datetime.datetime.strptime(request.GET.get('to'), "%Y-%m-%d")
    
    return dict(
        project=this_project,
        entity_filter=entity_filter,
        aspect_topic=aspect_topic,
        aspect_name=aspect_name,
        lang_filter=lang_filter,
        source_filter=source_filter,
        start=start,
        end=end,
        request=request
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


def get_chart_data(this_project, start, end, entity_filter, 
        aspect_topic, aspect_name, lang_filter, source_filter, request):

    result = {
        "status": "OK",
        "colors": charts.COLORS["contrasts"],
    }

    chart_classes = [
        charts.SentimentDonutChart,
        charts.SentimentTimeChart,
        charts.VolumeBySourceChart,
    ]

    if this_project.aspect_model:
        chart_classes.append(charts.AspectCooccurrence)

    for chart_class in chart_classes:
        instance = chart_class(
            this_project,
            start,
            end,
            entity_filter,
            aspect_topic,
            aspect_name,
            lang_filter,
            source_filter,
            request
        )
        
        chart_data = instance.render_data()
        result.update(chart_data)
    
    return result

@login_required(login_url=LOGIN_URL)
def projects(request, project_id):
    
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    end = this_project.data_set.latest().date_created
    start = end - datetime.timedelta(days=30)

    if 'from' in request.GET and 'to' in request.GET:
        start = datetime.datetime.strptime(
            request.GET.get('from'), "%Y-%m-%d")
        end = datetime.datetime.strptime(request.GET.get('to'), "%Y-%m-%d")
    
    context = {
        'project_id': project_id,
        'project': this_project,
        'total':this_project.data_set.count(),
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
    
    lang = request.GET.getlist('filter_language')
    if lang and lang[0]:
        lang_filter = lang[0].split(",")
        context['selected_langs'] = lang_filter
    else:
        lang_filter = None

    src = request.GET.getlist('filter_source')
    if src and src[0]:
        source_filter = src[0].split(",")
        context['selected_sources'] = source_filter
    else:
        source_filter = None
    
    entity_filter = request.GET.get('entity')
    aspect_topic = request.GET.get('aspecttopic')
    aspect_name = request.GET.get('aspectname')

    # Compute our aspect stats.
    ASPECT_QUERY = """
    SELECT 
        label, count(data_id),
        sum(case when data_aspect.sentiment > 0 then 1 else 0 end) as PosCount,
        sum(case when data_aspect.sentiment < 0 then 1 else 0 end) as NegCount
    FROM 
        data_aspect, data_data
    WHERE 
        %s
    GROUP BY label
    """
    context['aspect_data'] = []

    where_clause = [
        'data_aspect.data_id = data_data.id',
        'data_data.project_id = %s',
        'data_data.date_created between %s AND %s',
    ]
    query_args = [project_id, start, end]

    if lang_filter:
        lang_string = len(lang_filter) * '%s,'
        where_clause.append('data_data.language IN ({})'.format(lang_string[:-1]))
        query_args.extend(lang_filter)
    
    if source_filter:
        source_string = len(source_filter) * '%s,'
        where_clause.append('data_data.source_id IN ({})'.format(source_string[:-1]))
        # Get the raw IDs for our sources.
        source_ids = data_models.Source.objects.filter(
                label__in=source_filter).values_list('id', flat=True)
        query_args.extend(source_ids)
    
    if aspect_topic:
        where_clause.append('data_aspect.topic = %s')
        query_args.append(aspect_topic)
    
    if aspect_name:
        where_clause.append('data_aspect.label = %s')
        query_args.append(aspect_name)

    total = 0
    with connection.cursor() as cursor:
        cursor.execute(ASPECT_QUERY % ' AND '.join(where_clause), query_args)
        for idx, row in enumerate(cursor.fetchall()):
            total += row[1]
            context['aspect_data'].append({
                'label':row[0],
                'count':row[1],
                'pos': row[2],
                'neg': row[3],
                'color':ASPECT_COLORS[idx],
            })
    
    # Now calculate percent for each aspect.
    for a in context['aspect_data']:
        a['percent'] = round(100.0 * (float(a['count']) / float(total)), 2)
    
    chart_data = get_chart_data(
        this_project,
        start,
        end,
        entity_filter,
        aspect_topic,
        aspect_name,
        lang_filter,
        source_filter,
        request,
    )

    # Shove the aspect data into the chart data so it can render nicely in javascript.
    chart_data['aspect_data'] = context['aspect_data']

    context['total_data'] = chart_data['total_data']
    context['total_positive'] = chart_data['total_positive']
    context['total_negative'] = chart_data['total_negative']
    
    json_chart_data = json.dumps(chart_data, sort_keys=True, default=default_encoder)
    context['chart_data'] = json_chart_data

    # Find the earliest and latest date. This helps populate the view all link.
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT to_char(max(data_data.date_created), 'YYYY-MM-DD'), to_char(min(data_data.date_created), 'YYYY-MM-DD')
            FROM data_data
            WHERE data_data.project_id = %s""", [this_project.id])
        row = cursor.fetchone()
        context['latest'] = row[0]
        context['earliest'] = row[1]

    return render(request, "project.html", context)

@login_required(login_url=LOGIN_URL)
def new_projects(request):
    user = request.user
    projects = list(data_models.Project.objects.filter(users=user).values("name", "id"))
    for project in projects:
        data = data_models.Data.objects.filter(project=project["id"]).aggregate(
        positive_count=Coalesce(Sum(Case(When(sentiment__gt=0, then=1)), output_field=IntegerField()), 0), 
        negative_count=Coalesce(Sum(Case(When(sentiment__lt=0, then=1)), output_field=IntegerField()),0),
        neutral_count=Coalesce(Sum(Case(When(sentiment=0, then=1)), output_field=IntegerField()),0))
        #print(data)
        project.update(data)
        #print(project)
    context={}
    context["projects_data"] = projects
    context["projects_count"] = len(projects)
    return render(request, "projects.html", context)

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
    for a in aspects.values('sentiment_text', 'chunk', 'data__text'):
        for t in a['sentiment_text']:
            if t and t != topic:
                data.append([t, a['data__text']])
    
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

@login_required(login_url=LOGIN_URL)
def data_per_aspect(request, project_id):
    this_project = get_object_or_404(data_models.Project, pk=project_id)

    if this_project.users.filter(pk=request.user.id).count() == 0:
    # This user does not have permission to view this project.
        return HttpResponseForbidden()

    aspect_label = request.GET.get('aspect', '')
    sentiment = request.GET.get('sentiment', '')
    print(sentiment, aspect_label)
    with connection.cursor() as cursor:
        if sentiment == 'neutral':
            cursor.execute("""
                select distinct dd.sentiment , dd."text", da."label" from data_aspect da inner join data_data dd on da.data_id = dd.id where dd.project_id = %s and dd.sentiment = 0 and da."label" = %s""", [this_project.id, aspect_label])
        elif sentiment == 'negative':
            cursor.execute("""
                select distinct dd.sentiment , dd."text", da."label" from data_aspect da inner join data_data dd on da.data_id = dd.id where dd.project_id = %s and dd.sentiment < 0 and da."label" = %s""", [this_project.id, aspect_label])
        elif sentiment == 'positive':
            cursor.execute("""
                select distinct dd.sentiment , dd."text", da."label" from data_aspect da inner join data_data dd on da.data_id = dd.id where dd.project_id = %s and dd.sentiment > 0 and da."label" = %s""", [this_project.id, aspect_label])
        rows = cursor.fetchall()
        print(rows)
    return JsonResponse(rows, safe=False)

@login_required(login_url=LOGIN_URL)
def sentiment_per_entity(request, project_id):
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
    # This user does not have permission to view this project.
        return HttpResponseForbidden()
    entities_limit = request.GET.get("max-entities", 8)
    with connection.cursor() as cursor:
        cursor.execute("""
        select dde.entity_id, de."label" , count(dde.entity_id) from data_data_entities dde inner join data_data dd on dd.id = dde.data_id inner join data_entity de on dde.entity_id = de.id where dd.project_id = %s group by (dde.entity_id, de."label") order by count(dde.entity_id) desc limit %s;
        """, [this_project.id, entities_limit])
        rows = cursor.fetchall()
    response = []
    for row in rows:
        data = data_models.Data.objects.filter(entities__pk = row[0], project_id=project_id)
        negative_count = data.filter(sentiment__lt = 0).count()
        positive_count = data.filter(sentiment__gt = 0).count()
        neutral_count = data.filter(sentiment= 0).count()
        data_response = data.values("sentiment", "text")
        response.append({"positive_count": positive_count, "neutral_count":neutral_count, "negative_count": negative_count, "entity_label": row[1], "data":list(data_response)})

    return JsonResponse(response, safe=False)

@login_required(login_url=LOGIN_URL)
def topics_per_aspect(request, project_id):
    this_project = get_object_or_404(data_models.Project, pk=project_id)

    if this_project.users.filter(pk=request.user.id).count() == 0:
    # This user does not have permission to view this project.
        return HttpResponseForbidden()
    response_data = {'aspects':{}}
    with connection.cursor() as cursor:

        cursor.execute("""
            select da."label" ,da.topic, count(*) from data_aspect da inner join data_data dd on dd.id = da.data_id where dd.project_id = %s group by (da.topic, da."label") order by  da."label" ,count(*) desc;""", [project_id])
        rows = cursor.fetchall()
        #print(rows)
    for row in rows:
        if row[0] not in response_data['aspects']:
            response_data['aspects'][row[0]] = {}
            response_data['aspects'][row[0]]['topics'] = list()
        else:
            aux = {'topic': row[1], 'count': row[2]}
            response_data['aspects'][row[0]]['topics'].append(aux)
    return JsonResponse(response_data, safe=False)
