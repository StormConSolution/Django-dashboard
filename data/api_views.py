import datetime
import csv
import json
import math

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

import data.charts as charts
import data.models as data_models
from dashboard.tasks import process_data
from data.helpers import get_filters_sql, get_where_clauses, get_order_by

MAX_PAGE_SIZE = 100


def pagination_details(request):
    page_size = request.GET.get("page-size") or 10
    page = request.GET.get("page") or 1

    return int(page), int(page_size)


def validate_api_call(api_key, project_id):
    # Make sure apikey is valid for project.
    try:
        p = data_models.Project.objects.get(pk=project_id)
    except data_models.Project.DoesNotExist as e:
        return False, JsonResponse({
            "status": "Fail",
            "title": "Permission denied",
            "description": "You do not have access to this data"
        })

    if p.api_key != api_key:
        return False, JsonResponse({
            "status": "Fail",
            "title": "Permission denied",
            "description": "You do not have access to this data"
        })

    return True, None


@csrf_exempt
def project_operations(request, api_key):
    """
    API endpoint for creating a new project or fetching existing projects.
    """
    if request.method == 'POST':
        if 'name' not in request.POST or 'username' not in request.POST:
            return JsonResponse({"status": "Fail", "description": "Both `name` and `username` are required"})

        proj, _ = data_models.Project.objects.get_or_create(
            api_key=api_key,
            name=request.POST['name'],
        )

        if 'aspect_model' in request.POST:
            m, _ = data_models.AspectModel.objects.get_or_create(
                api_key=api_key,
                label=request.POST['aspect_model'])
            proj.aspect_model = m
            proj.save()

        try:
            user = User.objects.get(username__iexact=request.POST['username'])
        except User.DoesNotExist as e:
            return JsonResponse({
                "status": "Fail",
                "description": "Username not found",
                "title": "Project could not be added"})

        proj.users.add(user)

        return JsonResponse({"status": "OK", "project_id": proj.id})
    elif request.method == 'GET':
        projects = []
        for p in data_models.Project.objects.filter(api_key=api_key):
            projects.append({
                'name':p.name,
                'aspect_model':p.aspect_model and p.aspect_model.label or '',
                'id':p.id,
            })

        return JsonResponse({"status": "OK", "projects": projects})


@csrf_exempt
def data_operations(request, api_key, project_id):
    """
    API endpoint for adding or fetching data.

    Required: 
        text: the text itself

    Optional:
        date: date this item was created, defaults today
        lang: language of the text
        source: where did the text come from, create if doesn't exist
        url: URL of the original data source
    """
    if request.method == 'POST':
        for key in ('text', 'source'):
            if key not in request.POST:
                return JsonResponse({
                    "status": "Fail",
                    "title": "Data not added",
                    "description": "Missing required field `{}`".format(key)
                })

        has_permission, error = validate_api_call(api_key, project_id)
        if not has_permission:
            return error

        task_argument = {
            "project_id": project_id,
            "metadata": {},
        }

        for key in ('lang', 'date', 'source', 'url', 'text',):
            task_argument[key] = request.POST.get(key, '')

        if 'metadata' in request.POST:
            task_argument['metadata'] = json.loads(request.POST['metadata'])

        process_data.delay(task_argument)
        return JsonResponse({"status": "OK"})

    elif request.method in ('GET', 'DELETE'):
        page, page_size = pagination_details(request)
        page_size = min(page_size, MAX_PAGE_SIZE)

        query = {'project': project_id}

        if request.GET.get('date_from'):
            query['date_created__gte'] = request.GET['date_from']

        if request.GET.get('date_to'):
            query['date_created__lte'] = request.GET['date_to']

        if request.GET.get("metadata_key"):
            key = request.GET['metadata_key']
            if request.GET.get("metadata_value"):
                # A specific metadata value must match.
                query["metadata__{}".format(key)] = request.GET['metadata_value']
            else:
                # Checking to see the key is present regardless of value.
                query["metadata__has_key"] = key

        if request.GET.get("sources"):
            sources = request.GET.get("sources").split(",")
            query["source__label__in"] = sources

        if request.method == 'DELETE':
            total, _ = data_models.Data.objects.filter(**query).delete()
            return JsonResponse({'status':'OK', 'total':total})

        total = data_models.Data.objects.filter(**query).count()
        data = data_models.Data.objects.filter(
            **query).prefetch_related(
            'entities', 'aspect_set').order_by(
            '-date_created')[(page - 1) * page_size:(page - 1) * page_size + page_size]

        # Return data as JSON.
        json_data = {'status': 'OK', 'total': total, 'data': []}
        for obj in data:
            d = {
                'text': obj.text,
                'url': obj.url,
                'date_created': obj.date_created.strftime('%Y-%m-%d'),
                'source': obj.source.label,
                'sentiment': obj.sentiment,
                'language': obj.language,
                'metadata': obj.metadata,
                'aspects': list(obj.aspect_set.values('label', 'sentiment', 'chunk', 'topic', 'sentiment_text')),
                'entities': [],
            }

            for e in obj.entities.all():
                d['entities'].append({
                    'title': e.label,
                    'classifications': ','.join([c.label for c in e.classifications.all()])
                })

            json_data['data'].append(d)

        return JsonResponse(json_data)


@csrf_exempt
def metadata(request, api_key, project_id):
    # Make sure this project belongs to this API key.
    has_permission, error = validate_api_call(api_key, project_id)
    if not has_permission:
        return error

    key = request.GET.get("key")
    if not key:
        # Return all possible keys.
        with connection.cursor() as cursor:
            cursor.execute("""select distinct (jsonb_object_keys(dd.metadata))
            from data_data as dd where  dd.project_id = %s""", [project_id])
            rows = cursor.fetchall()

        response = {
            'status': 'OK',
            'keys': [k[0] for k in rows],
        }

        return JsonResponse(response)

    # A specific key was supplied, return the values for that key.
    with connection.cursor() as cursor:
        cursor.execute("""SELECT distinct(dd.metadata ->> %s)
        FROM data_data dd where dd.project_id = %s;
        """, [key, project_id])
        rows = cursor.fetchall()

    response = {
        'status': 'OK',
        'key': key,
        'values': [v[0] for v in rows]
    }

    return JsonResponse(response)


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def project_overview(request, project_id):
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied
    data = {}
    where_clauses = []
    where_clauses.append("dd.project_id = %s")
    query = """
            select distinct sum(case when dd.sentiment > 0 then 1 else 0 end) as positives ,sum(case when dd.sentiment < 0 then 1 else 0 end) as negatives, sum(case when dd.sentiment = 0 then 1 else 0 end) as neutrals from data_data dd inner join data_source ds on ds.id = dd.source_id where """ + get_where_clauses(
        request, where_clauses)
    with connection.cursor() as cursor:
        cursor.execute(query, [project_id])
        row = cursor.fetchone()
    data["positivesCount"] = row[0] or 0
    data["negativesCount"] = row[1] or 0
    data["neutralsCount"] = row[2] or 0
    data["aspectCount"] = data_models.Aspect.objects.filter(data__project=project_id).distinct('label').count()

    where_clauses = []
    where_clauses.append("dd.project_id = %s")
    with connection.cursor() as cursor:
        cursor.execute("""
            select count(distinct ds."label") from data_source ds inner join data_data dd on ds.id = dd.source_id where """ + " and ".join(
            where_clauses), [project.id])
        rows = cursor.fetchall()
    data["sourceCount"] = rows[0][0]
    return JsonResponse(data, safe=False)


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def volume_by_source(request, project_id):
    project = get_object_or_404(data_models.Project, pk=project_id)
    filtersSQL = get_filters_sql(request)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied
    where_clauses = [
        "dd.project_id = %s"
    ]
    with connection.cursor() as cursor:
        cursor.execute("""
            select distinct ds.id, ds."label" ,count(ds.id) from data_data dd inner join data_source ds on dd.source_id = ds.id where """ + get_where_clauses(
            request, where_clauses) + """ group by ds.id order by count(ds.id) desc limit 10;""", [project.id])
        rows = cursor.fetchall()
    response = []
    for row in rows:
        aux = {}
        aux["sourceID"] = row[0]
        aux["sourceName"] = row[1]
        aux["sourceCount"] = row[2]
        response.append(aux)
    return JsonResponse(response, safe=False)


def get_chart_data(this_project, start, end, entity_filter,
                   aspect_topic, aspect_name, lang_filter, source_filter, request):
    result = {
        "status": "OK",
        "colors": charts.COLORS["contrasts"],
    }

    chart_classes = []
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


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def co_occurence(request, project_id):
    context = {}
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    if data_models.Data.objects.filter(project_id=project_id).count() == 0:
        return JsonResponse({}, safe=False)

    start = request.GET.get("date_from")
    end = request.GET.get("date_to")
    if not start or not end:
        end = this_project.data_set.latest().date_created
        start = end - datetime.timedelta(days=30)

    source_filter = request.GET.get('sourcesID')
    if source_filter:
        source_filter = source_filter.split(',')

    lang_filter = request.GET.get("languages")
    if lang_filter:
        lang_filter = lang_filter.split(',')

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
    if "aspect_cooccurrence_data" in chart_data:
        response = chart_data["aspect_cooccurrence_data"]
    else:
        response = {}

    return JsonResponse(response, safe=False)


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def entity_classification_count(request, project_id):
    user = request.user
    page, page_size = pagination_details(request)

    project = get_object_or_404(data_models.Project, pk=project_id)
    aspect_label = request.GET.get("aspect-label", "")
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    filtersSQL = get_filters_sql(request)
    where_clause = [
        "dd.project_id = %s"
    ]
    query_args = [project_id]

    aspect_inner_join = ""
    if aspect_label != "":
        aspect_inner_join = 'inner join data_aspect da on da.data_id = dd.id'
        where_clause.append('da."label" = %s')
        query_args.append(aspect_label)

    with connection.cursor() as cursor:
        cursor.execute("""
        select count(distinct (dec2.classification_id , dec2.entity_id ) ) from data_entity de inner join data_entity_classifications dec2 on de.id = dec2.entity_id inner join data_classification dc on dc.id = dec2.classification_id inner join data_data_entities dde on dde.entity_id = de.id inner join data_data dd on dd.id = dde.data_id inner join data_source ds on dd.source_id = ds.id """ + aspect_inner_join + """ where """ + get_where_clauses(
            request, where_clause), query_args)
        row = cursor.fetchone()
    total = int(row[0])

    offset = (page - 1) * page_size
    total_pages = math.ceil(total / page_size)
    response_format = request.GET.get("format", "")
    query_args = [
        project_id
    ]
    aspect_inner_join = ""
    if aspect_label != "":
        aspect_inner_join = 'inner join data_aspect da on da.data_id = dd.id'
        query_args.append(aspect_label)

    limit_offset_clause = ""
    if response_format != "csv":
        limit_offset_clause = """limit %s offset %s;"""
        query_args.append(page_size)
        query_args.append(offset)

    with connection.cursor() as cursor:
        cursor.execute("""
            select de."label" , dc."label" , count(*) as frequency, de.id, dc.id  from data_entity de inner join data_entity_classifications dec2 on de.id = dec2.entity_id inner join data_classification dc on dc.id = dec2.classification_id inner join data_data_entities dde on dde.entity_id = de.id inner join data_data dd on dd.id = dde.data_id inner join data_source ds on dd.source_id = ds.id """ + aspect_inner_join + """ where """ + get_where_clauses(
            request, where_clause) + """ group by (de."label" , dc."label", de.id, dc.id)""" + get_order_by(request,
                                                                                                            "frequency",
                                                                                                            "desc") + limit_offset_clause,
                       query_args)
        rows = cursor.fetchall()

    if response_format == "csv":
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="data_items_entities_classification_frequency.csv"'

        writer = csv.writer(response)
        writer.writerow(['Entity', "Classification", "Frequency"])
        for row in rows:
            writer.writerow([row[0], row[1], row[2]])
        return response
    response = {}
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


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def aspect_topic(request, project_id):
    page, page_size = pagination_details(request)

    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    filtersSQL = get_filters_sql(request)
    where_clause = [
        "dd.project_id = %s"
    ]
    with connection.cursor() as cursor:
        cursor.execute("""
        select count(distinct (da."label", da.topic)) from data_aspect da inner join data_data dd on dd.id = da.data_id inner join data_source ds on dd.source_id = ds.id where da.topic != '' and """ + get_where_clauses(
            request, where_clause), [project.id])
        row = cursor.fetchone()
    total = int(row[0])

    offset = (page - 1) * page_size
    total_pages = math.ceil(total / page_size)
    response_format = request.GET.get("format", "")
    query_args = [
        project_id
    ]
    limit_offset_clause = ""
    if response_format != "csv":
        limit_offset_clause = """ limit %s offset %s;"""
        query_args.append(page_size)
        query_args.append(offset)
    with connection.cursor() as cursor:
        cursor.execute("""
            select distinct da."label", da.topic, count(dd.sentiment ) as c , sum (case when dd.sentiment > 0 then 1 else 0 end) as positives, sum (case when dd.sentiment < 0 then 1 else 0 end) as negatives from data_aspect da inner join data_data dd on dd.id = da.data_id inner join data_source ds on ds.id = dd.source_id where da.topic != '' and """ + get_where_clauses(
            request, where_clause) + """ group by (da.topic, da."label" ) """ + get_order_by(request, "c",
                                                                                             "desc") + limit_offset_clause,
                       query_args)
        rows = cursor.fetchall()
    if response_format == "csv":
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="aspect_topic_breakdown.csv"'

        writer = csv.writer(response)
        writer.writerow(['Topic', "Aspect", "Positives", "Negatives"])
        for row in rows:
            writer.writerow([row[1], row[0], row[3], row[4]])
        return response
    response = {}
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


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def sources_languages_per_project(request, project_id):
    """
    Fetch the unique set of languages and sources for this project.
    """
    project = data_models.Project.objects.get(pk=project_id)
    languages = list(project.data_set.values_list('language', flat=True).distinct())

    all_languages = []
    for l in languages:
        for code, label in settings.LANGUAGES:
            if l == code:
                all_languages.append({'code': code, 'label': label})

    all_languages = sorted(all_languages, key=lambda x: x['label'])
    all_sources = list(data_models.Source.objects.filter(
        pk__in=project.data_set.values_list('source', flat=True).distinct()).values())
    all_sources = sorted(all_sources, key=lambda x: x['label'])

    response = {
        "sources": all_sources,
        "languages": all_languages,
    }

    return JsonResponse(response, safe=False)
