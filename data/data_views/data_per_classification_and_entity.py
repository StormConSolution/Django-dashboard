import csv
import math

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404

from data.helpers import getWhereClauses, getFiltersSQL
import data.models as data_models

@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def data_per_classification_and_entity(request, project_id):
    page_size = int(request.GET.get("page-size", 10))
    page = int(request.GET.get("page", 1))
    aspect_label = request.GET.get("aspect-label", "")
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    entity = int(request.GET.get("entity"))
    classification = int(request.GET.get("classification"))
    where_clause = [
        "dd.project_id = %s",
        "de.id = %s",
        "dc.id = %s"
    ]

    query_args = [project.id, entity, classification]

    aspect_inner_join = ""
    if aspect_label != "":
        where_clause.append('da."label" = %s')
        aspect_inner_join = "inner join data_aspect da on da.data_id = dd.id"
        query_args.append(aspect_label)

    with connection.cursor() as cursor:
        cursor.execute("""
        select count(*) from data_data dd inner join data_data_entities dde on dd.id = dde.data_id inner join data_entity de on dde.entity_id = de.id inner join data_entity_classifications dec2 on de.id = dec2.entity_id inner join data_classification dc on dec2.classification_id = dc.id inner join data_source ds on dd.source_id = ds.id """ + aspect_inner_join + """ where """ + getWhereClauses(request, where_clause),
                       query_args)
        row = cursor.fetchone()
    total = int(row[0])

    offset = (page - 1) * page_size
    total_pages = math.ceil(total / page_size)

    response_format = request.GET.get("format", "")
    limit_offset_clause = ""

    if response_format == "":
        limit_offset_clause = """ limit %s offset %s;"""
        query_args.append(page_size)
        query_args.append(offset)

    if response_format == "word-cloud":
        with connection.cursor() as cursor:
            cursor.execute("""
            WITH counts AS (
            SELECT keyword, ct::INT from data_data dd CROSS JOIN LATERAL each(keywords) AS k(keyword, ct) inner join data_data_entities dde on dd.id = dde.data_id inner join data_entity de on dde.entity_id = de.id inner join data_entity_classifications dec2 on de.id = dec2.entity_id inner join data_classification dc on dec2.classification_id = dc.id inner join data_source ds on dd.source_id = ds.id """ + aspect_inner_join + """  where """ + getWhereClauses(request, where_clause) + """ order by date_created desc """ + limit_offset_clause + ") SELECT keyword, SUM(ct)::INT keyword_count FROM counts GROUP BY keyword ORDER BY keyword_count desc limit 50", query_args)
            rows = cursor.fetchall()
            response = []
            for row in rows:
                response.append({
                    'keyword':row[0],
                    'keywordCount':row[1],
                })
            return JsonResponse(response, safe=False)

    with connection.cursor() as cursor:
        cursor.execute("""
        select dd.date_created, dd."text" , dd."url", ds."label" , dd.weighted_score , dd.sentiment , dd."language" from data_data dd inner join data_data_entities dde on dd.id = dde.data_id inner join data_entity de on dde.entity_id = de.id inner join data_entity_classifications dec2 on de.id = dec2.entity_id inner join data_classification dc on dec2.classification_id = dc.id inner join data_source ds on dd.source_id = ds.id """+ aspect_inner_join+""" where """ + getWhereClauses(request, where_clause) + """ order by dd.date_created desc """ + limit_offset_clause,
                       query_args)
        rows = cursor.fetchall()

    if response_format == "csv":
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="data_per_classification_and_entity.csv"'

        writer = csv.writer(response)
        writer.writerow(['Date', "Text", "URL", "Source", "Weighted", "Raw", "Language"])
        for row in rows:
            writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6]])
        return response

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
            "url": row[2],
            "sourceLabel": row[3],
            "weightedScore": row[4],
            "sentimentValue": row[5],
            "languageCode": row[6]
        })

    return JsonResponse(response, safe=False)
