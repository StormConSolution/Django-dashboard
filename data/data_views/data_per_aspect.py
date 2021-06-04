import math
import csv
from urllib import parse

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404

import data.models as data_models
from data.helpers import getWhereClauses

@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def data_per_aspect(request, project_id):
    page_size = int(request.GET.get("page-size", 10))
    page = int(request.GET.get("page", 1))
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    aspect_label = parse.unquote(request.GET.get("aspect-label"))
    sentiment = request.GET.get("sentiment", "")

    response_format = request.GET.get("format", "")

    where_clause = [
        "dd.project_id = %s",
        "da.data_id = dd.id",
        "da.label = %s"
    ]
    if sentiment == "positive":
        where_clause.append("dd.sentiment > 0")
    if sentiment == "negative":
        where_clause.append("dd.sentiment < 0")
    if sentiment == "neutral":
        where_clause.append("dd.sentiment = 0")
    with connection.cursor() as cursor:
        cursor.execute("""
            select count(*) from data_data dd inner join data_source ds on ds.id = dd.source_id inner join data_aspect da on da.data_id = dd.id where """ + getWhereClauses(request, where_clause), [project.id, aspect_label])
        row = cursor.fetchone()
    total_data = int(row[0])

    offset = (page - 1) * page_size
    total_pages = math.ceil(total_data / page_size)

    limit_offset_clause = ""
    query_args = []
    query_args.append(project_id)
    query_args.append(aspect_label)
    if response_format == "":
        limit_offset_clause = """ limit %s offset %s """
        query_args.append(page_size)
        query_args.append(offset)
    if response_format == "word-cloud":
        with connection.cursor() as cursor:
            cursor.execute("""
                        WITH counts AS (
            SELECT keyword, ct::INT from data_data dd CROSS JOIN LATERAL each(keywords) AS k(keyword, ct) inner join data_source ds on dd.source_id = ds.id inner join data_aspect da on da.data_id = dd.id where """ + getWhereClauses(request, where_clause) + """ order by date_created desc """ + limit_offset_clause + ") SELECT keyword, SUM(ct)::INT keyword_count FROM counts GROUP BY keyword ORDER BY keyword_count desc limit 50", query_args)
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
            select dd.date_created, dd."text" , dd."url", ds."label" , dd.weighted_score , dd.sentiment , dd."language" from data_data dd inner join data_source ds on dd.source_id = ds.id inner join data_aspect da on da.data_id = dd.id where """ + getWhereClauses(request, where_clause) + """order by date_created desc """ + limit_offset_clause, query_args)
        rows = cursor.fetchall()
    if response_format == "csv":
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="data_items_per_aspect.csv"'

        writer = csv.writer(response)
        writer.writerow(['Date', "Text", "URL", "Source", "Weighted", "Raw", "Language"])
        for row in rows:
            writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6]])
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
            "url": row[2],
            "sourceLabel": row[3],
            "weightedScore": row[4],
            "sentimentValue": row[5],
            "languageCode": row[6]
        })

    return JsonResponse(response, safe=False)
