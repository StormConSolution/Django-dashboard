import datetime
import json
import math
import data.charts as charts
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from .permissions import IsAllowedAccessToData
import data.models as data_models
from data import serializers
from data import weighted
from django.db.models.functions import Coalesce
from django.db.models import Count, Q, F, Sum, Case, When, Value, IntegerField
from urllib import parse
from django.db import connection
LOGIN_URL = '/login/'

ASPECT_COLORS = [
    'Pink', 'Crimson', 'Coral', 'Chocolate', 'DarkCyan', 'LightCoral',
    'DarkOliveGreen', 'LightSkyBlue', 'MintCream', 'PowderBlue', 'SandyBrown',
    'Tomato', 'SeaGreen', 'DarkKhaki', 'DarkOrange', 'DarkSlateGray',
    'DeepSkyBlue', 'DimGrey', 'DarkRed', 'Gold', 'IndianRed', 'Lavender',
    'LightGrat', 'LightSlateGray',
]

def default_encoder(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()

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

class DataViewSet(viewsets.ModelViewSet):
    queryset = data_models.Data.objects.all()
    serializer_class = serializers.DataSerializer
    permission_classes = [IsAllowedAccessToData]


country_param = openapi.Parameter('country', in_=openapi.IN_QUERY, description='Filter By Country',
                                  type=openapi.TYPE_STRING)
source_param = openapi.Parameter('source', in_=openapi.IN_QUERY, description='Filter By Source',
                                 type=openapi.TYPE_STRING)
language_param = openapi.Parameter('language', in_=openapi.IN_QUERY, description='Filter By Language',
                                   type=openapi.TYPE_STRING)
date_created_param = openapi.Parameter('date_created',
                                       in_=openapi.IN_QUERY,
                                       description='Filter By Created Period. Example: :start_date,:end_date. Here '
                                                   'start_date and end_date can be empty', type=openapi.TYPE_STRING)


class ProjectDataListView(ListAPIView):
    serializer_class = serializers.DataSerializer
    permission_classes = [IsAllowedAccessToData]

    def get_queryset(self):
        filters = {
            'project_id': self.request.parser_context.get('kwargs', {}).get('project_id')
        }

        if self.request.query_params.get('country'):
            filters['country__label'] = self.request.query_params.get(
                'country')

        if self.request.query_params.get('source'):
            filters['source__label'] = self.request.query_params.get('source')

        if self.request.query_params.get('date_created'):
            start_date, end_date = self.request.query_params.get(
                'date_created').split(',')

            if start_date:
                filters['date_created__gt'] = start_date
            if end_date:
                filters['date_created__lt'] = end_date

        if self.request.query_params.get('language'):
            filters['language'] = self.request.query_params.get('language')

        return data_models.Data.objects.filter(**filters)

    @swagger_auto_schema(manual_parameters=[country_param, source_param, language_param, date_created_param])
    def get(self, request, *args, **kwargs):
        return super(ProjectDataListView, self).get(request, *args, **kwargs)


class SourceListAPI(ListAPIView):
    queryset = data_models.Source.objects.all()
    serializer_class = serializers.SourceSerializer


class CountryListAPI(ListAPIView):
    queryset = data_models.Country.objects.all()
    serializer_class = serializers.CountrySerializer


class ProjectListView(ListAPIView):
    serializer_class = serializers.ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return data_models.Project.objects.filter(users=self.request.user)


@csrf_exempt
def create_project(request):
    """
    API endpoint for creating a project. May need some work as we go.

    `name`: the name of the Project. If it doesn't exist, create it.
    `username`: the user name to add to this project. User is assumed to exist.
    `aspect_model`: the aspect model this project will use.
    """
    if 'name' not in request.POST or 'username' not in request.POST:
        return JsonResponse({"status": "Fail", "description": "Both `name` and `username` are required"})

    proj, _ = data_models.Project.objects.get_or_create(
        name=request.POST['name'])

    if 'aspect_model' in request.POST:
        m, _ = data_models.AspectModel.objects.get_or_create(
            label=request.POST['aspect_model'])
        proj.aspect_model = m
        proj.save()

    user, _ = User.objects.get_or_create(username=request.POST['username'])
    proj.users.add(user)

    return JsonResponse({"status": "OK", "project_id": proj.id})


@csrf_exempt
def add_data(request, project_id):
    """
    API endpoint for loading data. May need some work as we go.

    Required: 
        text: the text itself
        source: where did the text come from, create if doesn't exist

    Optional:
        country: the country this data came from
        with_entities=0/1: should we extract entities
        lang: language of the text
        url: URL of the original data source
        date: date this item was created, defaults today
        weight_args: the arguments to supply to the weighting formula, varies
            based on weight_type. Supplied as a JSON string.
    """
    for key in ('text', 'source'):
        if key not in request.POST:
            return JsonResponse({
                "status": "Fail",
                "message": "Missing required field `{}`".format(key)
            })

    text = request.POST['text']
    lang = request.POST.get('lang', 'en')

    try:
        resp = requests.post('{HOST}/v4/{APIKEY}/all.json'.format(
            HOST=settings.API_HOST, APIKEY=settings.APIKEY), data={'text': text, 'lang': lang}).json()
        if 'score' in resp:
            sentiment = resp['score']
        else:
            return JsonResponse(resp)
    except Exception as e:
        return JsonResponse({"status": "Fail", "message": "Could not add text = {} lang = {} because: {}".format(text, lang, e)})

    project = data_models.Project.objects.get(pk=project_id)

    source, _ = data_models.Source.objects.get_or_create(
        label=request.POST['source'])

    weight_args = json.loads(request.POST.get('weight_args', '{}'))
    weight_args['raw_score'] = sentiment
    weighted_score = weighted.calculate(**weight_args)

    data = data_models.Data.objects.create(
        date_created=request.POST.get('date', datetime.datetime.now().date()),
        project=project,
        source=source,
        text=text,
        sentiment=sentiment,
        weighted_score=weighted_score,
        language=lang,
        url=request.POST.get('url', ''),
    )

    metadata = request.POST.get('metadata')
    if metadata:
        data.metadata = json.loads(metadata)
        data.save()

    if request.POST.get('country'):
        country, _ = data_models.Country.objects.get_or_create(
            label=request.POST['country'])
        data.country = country
        data.save()

    if request.POST.get('with_entities'):
        for ent in resp['entities']:
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

    return JsonResponse({"status": "OK"})


@login_required(login_url=LOGIN_URL)
def project_overview(request, project_id):
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied
    data = {}
    dateFrom = request.GET.get("date-from")
    dateTo = request.GET.get("date-to")
    if not dateFrom:
        dateFrom = ""
    if not dateTo:
        dateTo = ""
    filters = []
    if dateFrom != "" :
        filters.append("dd.date_created > '" + dateFrom + "'")
    if dateTo != "":
        filters.append("dd.date_created < '" + dateTo + "'")
    filtersSQL = " and ".join(filters)
    if filtersSQL != "":
        filtersSQL = " and " + filtersSQL
    else:
        filterSQL = ""

    query = """
            select sum(case when dd.sentiment > 0 then 1 else 0 end) as positives ,sum(case when dd.sentiment < 0 then 1 else 0 end) as negatives, sum(case when dd.sentiment = 0 then 1 else 0 end) as neutrals from data_data dd where dd.project_id = %s""" + filtersSQL
    with connection.cursor() as cursor:
        cursor.execute(query, [project.id])
        row = cursor.fetchone()
    data["positivesCount"] = row[0] or 0
    data["negativesCount"] = row[1] or 0
    data["neutralsCount"] = row[2] or 0
    with connection.cursor() as cursor:
        cursor.execute("""
            select count(*) from data_aspectlabel_source das where das.project_id = %s;""", [project.id])
        rows = cursor.fetchall()
    data["aspectCount"] = rows[0][0]
    with connection.cursor() as cursor:
        cursor.execute("""
            select count(distinct ds."label") from data_source ds inner join data_data dd on ds.id = dd.source_id where dd.project_id = %s;""", [project.id])
        rows = cursor.fetchall()
    data["sourceCount"] = rows[0][0]
    return JsonResponse(data, safe=False)

@login_required(login_url=LOGIN_URL)
def volume_by_source(request, project_id):
    user = request.user
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied
    data = data_models.Data.objects.filter(project=project).aggregate(
        positive_count=Coalesce(
            Sum(Case(When(sentiment__gt=0, then=1)), output_field=IntegerField()), 0),
        negative_count=Coalesce(
            Sum(Case(When(sentiment__lt=0, then=1)), output_field=IntegerField()), 0),
        neutral_count=Coalesce(Sum(Case(When(sentiment=0, then=1)), output_field=IntegerField()), 0))
    context = {}
    return JsonResponse(data, safe=False)

@login_required(login_url=LOGIN_URL)
def volume_by_source(request, project_id):
    user = request.user
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied
    with connection.cursor() as cursor:
        cursor.execute("""
            select distinct ds.id, ds."label" ,count(ds.id) from data_data dd inner join data_source ds on dd.source_id = ds.id where dd.project_id = %s group by ds.id;""", [project.id])
        rows = cursor.fetchall()
    response = []
    for row in rows:
        aux = {}
        aux["sourceName"] = row[1]
        aux["sourceCount"] = row[2]
        response.append(aux)
    return JsonResponse(response, safe=False)

@login_required(login_url=LOGIN_URL)
def aspect_count(request, project_id):
    user = request.user
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied
    with connection.cursor() as cursor:
        cursor.execute("""
            select distinct da."label", count(da."label")  from data_data dd inner join data_aspect da on dd.id = da.data_id where dd.project_id = %s group by da."label" order by count(da."label") desc ;""", [project.id])
        rows = cursor.fetchall()
    response = []
    for row in rows:
        aux = {}
        aux["aspectLabel"] = row[0]
        aux["aspectCount"] = row[1]
        response.append(aux)
    return JsonResponse(response, safe=False)

@login_required(login_url=LOGIN_URL)
def co_occurence(request, project_id):
    context = {}
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    end = this_project.data_set.latest().date_created
    start = end - datetime.timedelta(days=30)

    # list of languages in a given project
    lan_data = list(data_models.Data.objects.filter(
        project=this_project).values('language').distinct())
    lang_list = []
    for lan in lan_data:
        lang_list.append(lan['language'])
    
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
    return JsonResponse(chart_data["aspect_cooccurrence_data"], safe=False)

@login_required(login_url=LOGIN_URL)
def sentiment_per_aspect(request, project_id):
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied
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
    entity_filter = request.GET.get('entity')
    aspect_topic = request.GET.get('aspecttopic')
    aspect_name = request.GET.get('aspectname')
    src = request.GET.getlist('filter_source')
    if src and src[0]:
        source_filter = src[0].split(",")
        context['selected_sources'] = source_filter
    else:
        source_filter = None
    end = this_project.data_set.latest().date_created
    start = end - datetime.timedelta(days=30)
    where_clause = [
        'data_aspect.data_id = data_data.id',
        'data_data.project_id = %s',
        'data_data.date_created between %s AND %s',
    ]
    query_args = [project_id, start, end]
    lang = request.GET.getlist('filter_language')
    if lang and lang[0]:
        lang_filter = lang[0].split(",")
        context['selected_langs'] = lang_filter
    else:
        lang_filter = None

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
    response = []
    with connection.cursor() as cursor:
        cursor.execute(ASPECT_QUERY % ' AND '.join(where_clause), query_args)
        for idx, row in enumerate(cursor.fetchall()):
            total += row[1]
            response.append({
                'aspectLabel':row[0],
                'count':row[1],
                'positiveCount': row[2],
                'negativeCount': row[3],
            })
    return JsonResponse(response, safe=False)

@login_required(login_url=LOGIN_URL)
def data(request, project_id):
    user = request.user
    page_size = int(request.GET.get("page-size", 10))
    page = int(request.GET.get("page", 1))
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    with connection.cursor() as cursor:
        cursor.execute("""
            select count(*) from data_data where project_id = %s;""", [project.id])
        row = cursor.fetchone()
    total_data = int(row[0])

    offset = (page - 1) * page_size
    total_pages = math.ceil(total_data / page_size)

    with connection.cursor() as cursor:
        cursor.execute("""
            select dd.date_created, dd."text" , ds."label" , dd.weighted_score , dd.sentiment , dd."language" from data_data dd inner join data_source ds on dd.source_id = ds.id where project_id = %s order by date_created desc limit %s offset %s;""", [project.id, page_size, offset])
        rows = cursor.fetchall()
    
    response={}
    response["data"] = []
    response["currentPage"] = page
    response["totalData"] = total_data
    response["totalPages"] = total_pages
    response["pageSize"] = page_size
    for row in rows:
        response["data"].append({
            "dateCreated": row[0],
            "text": row[1],
            "sourceLabel": row[2],
            "weightedScore": row[3],
            "sentimentValue": row[4],
            "languageCode": row[5]
        })

    return JsonResponse(response, safe=False)

@login_required(login_url=LOGIN_URL)
def entity_classification_count(request, project_id):
    user = request.user
    page_size = int(request.GET.get("page-size", 10))
    page = int(request.GET.get("page", 1))
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied


    with connection.cursor() as cursor:
        cursor.execute("""
        select count(distinct (dec2.classification_id , dec2.entity_id ) ) from data_entity de inner join data_entity_classifications dec2 on de.id = dec2.entity_id inner join data_classification dc on dc.id = dec2.classification_id inner join data_data_entities dde on dde.entity_id = de.id inner join data_data dd on dd.id = dde.data_id where dd.project_id = %s;""", [project.id])
        row = cursor.fetchone()
    total = int(row[0])

    offset = (page - 1) * page_size
    total_pages = math.ceil(total / page_size)

    with connection.cursor() as cursor:
        cursor.execute("""
            select de."label" , dc."label" , count(*), de.id, dc.id  from data_entity de inner join data_entity_classifications dec2 on de.id = dec2.entity_id inner join data_classification dc on dc.id = dec2.classification_id inner join data_data_entities dde on dde.entity_id = de.id inner join data_data dd on dd.id = dde.data_id where dd.project_id = %s group by (de."label" , dc."label", de.id, dc.id) order by count(*) desc limit %s offset %s;
""", [project.id, page_size, offset])
        rows = cursor.fetchall()
    
    response={}
    response["data"] = []
    response["currentPage"] = page
    response["total"] = total
    response["totalPages"] = total_pages
    response["pageSize"] = page_size
    for row in rows:
        response["data"].append({
            "entityLabel": row[0],
            "entityID": row[3],
            "classificationLabel": row[1],
            "classificationID": row[4],
            "count": row[2]
        })

    return JsonResponse(response, safe=False)

@login_required(login_url=LOGIN_URL)
def aspect_topic(request, project_id):
    page_size = int(request.GET.get("page-size", 10))
    page = int(request.GET.get("page", 1))
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    with connection.cursor() as cursor:
        cursor.execute("""
        select count(distinct (da."label", da.topic)) from data_aspect da inner join data_data dd on dd.id = da.data_id where dd.project_id = %s;""", [project.id])
        row = cursor.fetchone()
    total = int(row[0])

    offset = (page - 1) * page_size
    total_pages = math.ceil(total / page_size)

    with connection.cursor() as cursor:
        cursor.execute("""
            select da."label", da.topic, count(dd.sentiment ) as c , sum (case when dd.sentiment > 0 then 1 else 0 end) as positives, sum (case when dd.sentiment < 0 then 1 else 0 end) as negatives from data_aspect da inner join data_data dd on dd.id = da.data_id where dd.project_id = %s group by (da.topic, da."label" ) order by c desc limit %s offset %s;""", [project.id, page_size, offset])
        rows = cursor.fetchall()
    
    response={}
    response["data"] = []
    response["currentPage"] = page
    response["total"] = total
    response["totalPages"] = total_pages
    response["pageSize"] = page_size
    for row in rows:
        response["data"].append({
            "aspectLabel": row[0],
            "topicLabel": row[1],
            "positivesCount": row[3],
            "negativesCount": row[4]
        })

    return JsonResponse(response, safe=False)

@login_required(login_url=LOGIN_URL)
def sentiment_trend(request, project_id):
    user = request.user
    page_size = int(request.GET.get("page-size", 10))
    page = int(request.GET.get("page", 1))
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    with connection.cursor() as cursor:
        cursor.execute("""
        select count(distinct (da."label", da.topic)) from data_aspect da inner join data_data dd on dd.id = da.data_id where dd.project_id = %s;""", [project.id])
        row = cursor.fetchone()
    total = int(row[0])

    offset = (page - 1) * page_size
    total_pages = math.ceil(total / page_size)

    with connection.cursor() as cursor:
        cursor.execute("""
            select dates.date, sum(case when dd.sentiment > 0 then 1 else 0 end) as positives , sum(case when dd.sentiment < 0 then 1 else 0 end) as negatives from (select distinct(to_char (dd.date_created, 'YYYY-MM')) as date from data_data dd where dd.project_id = %s order by date desc limit 7) as dates inner join data_data dd on to_char (dd.date_created, 'YYYY-MM') = dates.date where dd.project_id = %s group by dates.date order by dates.date asc;""", [project.id, project_id])
        rows = cursor.fetchall()
    
    response=[]
    for row in rows:
        response.append({
            "date": row[0],
            "positivesCount": row[1],
            "negativesCount": row[2]
        })


    return JsonResponse(response, safe=False)


@login_required(login_url=LOGIN_URL)
def data_per_classification_and_entity(request, project_id):
    user = request.user
    page_size = int(request.GET.get("page-size", 10))
    page = int(request.GET.get("page", 1))
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    entity = int(request.GET.get("entity"))
    classification = int(request.GET.get("classification"))
    with connection.cursor() as cursor:
        cursor.execute("""
        select count(*) from data_data dd inner join data_data_entities dde on dd.id = dde.data_id inner join data_entity de on dde.entity_id = de.id inner join data_entity_classifications dec2 on de.id = dec2.entity_id inner join data_classification dc on dec2.classification_id = dc.id inner join data_source ds on dd.source_id = ds.id where dd.project_id = %s and de.id = %s and dc.id = %s;""",
                       [project.id, entity, classification])
        row = cursor.fetchone()
    total = int(row[0])

    offset = (page - 1) * page_size
    total_pages = math.ceil(total / page_size)

    with connection.cursor() as cursor:
        cursor.execute("""
        select dd.date_created, dd."text" , ds."label" , dd.weighted_score , dd.sentiment , dd."language" from data_data dd inner join data_data_entities dde on dd.id = dde.data_id inner join data_entity de on dde.entity_id = de.id inner join data_entity_classifications dec2 on de.id = dec2.entity_id inner join data_classification dc on dec2.classification_id = dc.id inner join data_source ds on dd.source_id = ds.id where dd.project_id = %s and de.id = %s and dc.id = %s order by dd.date_created desc limit %s offset %s;""",
                       [project.id, entity, classification, page_size, offset])
        rows = cursor.fetchall()

    response = {}
    response["data"] = []
    response["currentPage"] = page
    response["total"] = total
    response["totalPages"] = total_pages
    response["pageSize"] = page_size
    response["entity"] = entity
    response["classification"] = classification
    for row in rows:
        response["data"].append({
            "dateCreated": row[0],
            "text": row[1],
            "sourceLabel": row[2],
            "weightedScore": row[3],
            "sentimentValue": row[4],
            "languageCode": row[5]
        })

    return JsonResponse(response, safe=False)

@login_required(login_url=LOGIN_URL)
def data_per_aspect_topic(request, project_id):
    user = request.user
    page_size = int(request.GET.get("page-size", 10))
    page = int(request.GET.get("page", 1))
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    aspect_label = parse.unquote(request.GET.get("aspect-label"))
    topic_label = parse.unquote(request.GET.get("topic-label"))
    sentiment = request.GET.get("sentiment")
    sentiment_filter = ""
    if sentiment == "positive":
        sentiment_filter = "and dd.sentiment > 0"
    elif sentiment == "negative":
        sentiment_filter = "and dd.sentiment < 0"

    count_query = """select count(*) from data_data dd inner join data_aspect da on dd.id = da.data_id where dd.project_id = %s and da."label" = %s and da.topic =%s """ + sentiment_filter
    with connection.cursor() as cursor:
        cursor.execute("""select count(*) from data_data dd inner join data_aspect da on dd.id = da.data_id where dd.project_id = %s and da."label" = %s and da.topic = %s """ + sentiment_filter,
                       [project.id, aspect_label, topic_label])

        row = cursor.fetchone()
    total = int(row[0])
    offset = (page - 1) * page_size
    total_pages = math.ceil(total / page_size)

    query = """ select dd.date_created, dd."text" , ds."label" , dd.weighted_score , dd.sentiment , dd."language" from data_data dd inner join data_aspect da on dd.id = da.data_id inner join data_source ds on dd.source_id = ds.id where dd.project_id = %s and da."label" = %s and da.topic =%s """ + sentiment_filter + """ order by dd.date_created desc limit %s offset %s """

    with connection.cursor() as cursor:
        cursor.execute(query,
                       [project.id, aspect_label, topic_label, page_size, offset])
        rows = cursor.fetchall()

    response = {}
    response["data"] = []
    response["currentPage"] = page
    response["total"] = total
    response["totalPages"] = total_pages
    response["pageSize"] = page_size
    response["topicLabel"] = topic_label
    response["aspectLabel"] = aspect_label
    for row in rows:
        response["data"].append({
            "dateCreated": row[0],
            "text": row[1],
            "sourceLabel": row[2],
            "weightedScore": row[3],
            "sentimentValue": row[4],
            "languageCode": row[5]
        })
    return JsonResponse(response, safe=False)
