import csv
import math

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404

import data.models as data_models
from data.helpers import getWhereClauses

@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def data(request, project_id):
    page_size = int(request.GET.get("page-size", 10))
    page = int(request.GET.get("page", 1))
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    where_clause = [
        "dd.project_id = %s"
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
            select count(*) from data_data dd inner join data_source ds on ds.id = dd.source_id where """ + getWhereClauses(request, where_clause), [project_id])
        row = cursor.fetchone()
    total_data = int(row[0])

    offset = (page - 1) * page_size
    total_pages = math.ceil(total_data / page_size)

    where_clause = [
        "dd.project_id = %s"
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
        project_id
    ]
    limit_offset_clause = ""

    if response_format == "word-cloud":
        with connection.cursor() as cursor:
            cursor.execute("""
                with counts as ( SELECT keyword, ct::int from data_data dd CROSS JOIN LATERAL each(keywords) AS k(keyword, ct) inner join data_source ds on dd.source_id = ds.id where """ + getWhereClauses(request, where_clause) + """order by date_created desc ) SELECT keyword, SUM(ct)::INT keyword_count FROM counts GROUP BY keyword ORDER BY keyword_count desc limit 50""" + limit_offset_clause, query_args)
            rows = cursor.fetchall()
            response = []
            for row in rows:
                response.append({
                    'keyword':row[0],
                    'keywordCount':row[1],
                })
            return JsonResponse(response, safe=False)
    if response_format == "":
        limit_offset_clause = """ limit %s offset %s;"""
        query_args.append(page_size)
        query_args.append(offset)

    with connection.cursor() as cursor:
        cursor.execute("""
            select dd.date_created, dd."text" , ds."label" , dd.weighted_score , dd.sentiment , dd."language" from data_data dd inner join data_source ds on dd.source_id = ds.id where """ + getWhereClauses(request, where_clause) + """order by date_created desc""" + limit_offset_clause, query_args)
        rows = cursor.fetchall()
    
    if response_format == "csv":
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="data_items.csv"'

        writer = csv.writer(response)
        writer.writerow(['Date', "Text", "Source", "Weighted", "Raw", "Language"])
        for row in rows:
            writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5]])
        return response
    response={}
    response["data"] = []
    response["currentPage"] = page
    response["total"] = total_data
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
