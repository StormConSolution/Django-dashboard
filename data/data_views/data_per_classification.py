import csv
import math

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404

import data.models as data_models
from data.helpers import getWhereClauses, getFiltersSQL


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def data_per_classification(request, project_id):
    page_size = int(request.GET.get("page-size", 10))
    page = int(request.GET.get("page", 1))
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied
    classification_id = int(request.GET.get("classificationID", ""))
    where_clause = [
        "dd.project_id = %s",
        "dc.id = %s"
    ]

    sentiment = request.GET.get("sentiment", "")

    if sentiment == "positive":
        where_clause.append("dd.sentiment > 0")
    if sentiment == "negative":
        where_clause.append("dd.sentiment < 0")
    if sentiment == "neutral":
        where_clause.append("dd.sentiment = 0")

    with connection.cursor() as cursor:
        cursor.execute("""
            select count(dd.id) from data_classification dc inner join data_entity_classifications dec2 on dc.id = dec2.classification_id inner join data_data_entities dde ON dde.entity_id = dec2.entity_id inner join data_data dd on dd.id = dde.data_id inner join data_source ds on ds.id = dd.source_id where """ + getWhereClauses(request, where_clause), [project_id, classification_id])
        row = cursor.fetchone()
    total_data = int(row[0])

    offset = (page - 1) * page_size
    total_pages = math.ceil(total_data / page_size)

    where_clause = [
        "dd.project_id = %s",
    ]
    sentiment = request.GET.get("sentiment", "")

    if sentiment == "positive":
        where_clause.append("dd.sentiment > 0")
    if sentiment == "negative":
        where_clause.append("dd.sentiment < 0")
    if sentiment == "neutral":
        where_clause.append("dd.sentiment = 0")
    
    response_format = request.GET.get("format", "")
    query_args = [
        classification_id,
        project_id,
    ]
    limit_offset_clause = ""

    if response_format == "word-cloud":
        with connection.cursor() as cursor:
            cursor.execute("""
                with counts as ( SELECT keyword, ct::int from data_data dd CROSS JOIN LATERAL each(keywords) AS k(keyword, ct) inner join data_classification dc on dc.id=%s inner join data_entity_classifications dec2 on dc.id = dec2.classification_id inner join data_data_entities dde ON dde.entity_id = dec2.entity_id inner join data_source ds on ds.id = dd.source_id where dd.id= dde.data_id and """ + getWhereClauses(request, where_clause) + """order by date_created desc ) SELECT keyword, SUM(ct)::INT keyword_count FROM counts GROUP BY keyword ORDER BY keyword_count desc limit 50""" + limit_offset_clause, query_args)
            rows = cursor.fetchall()
            response = []
            for row in rows:
                response.append({
                    'keyword':row[0],
                    'keywordCount':row[1],
                })
            return JsonResponse(response, safe=False)
    query_args = [
        project_id,
        classification_id,
    ]
    if response_format == "":
        limit_offset_clause = """ limit %s offset %s;"""
        query_args.append(page_size)
        query_args.append(offset)
    where_clause = [
        "dd.project_id = %s",
        "dc.id = %s"
    ]
    with connection.cursor() as cursor:
        cursor.execute("""select dd.date_created, dd."text", dd."url", ds."label", dd.weighted_score , dd.sentiment , dd."language" from data_classification dc inner join data_entity_classifications dec2 on dc.id = dec2.classification_id inner join data_data_entities dde ON dde.entity_id = dec2.entity_id inner join data_data dd on dd.id = dde.data_id inner join data_source ds on ds.id = dd.source_id where """ + getWhereClauses(request, where_clause) + """ order by dd.date_created desc """ + limit_offset_clause, query_args)
        rows = cursor.fetchall()
    
    if response_format == "csv":
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="data_items.csv"'

        writer = csv.writer(response)
        writer.writerow(['Date', "Text", "URL", "Source", "Weighted", "Raw", "Language"])
        for row in rows:
            writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6]])
        return response

    response = {}
    response["data"] = []
    response["currentPage"] = page
    response["total"] = total_data
    response["totalPages"] = total_pages
    response["pageSize"] = page_size
    
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