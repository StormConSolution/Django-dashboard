from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from data.helpers import getWhereClauses
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse, HttpResponse
import data.models as data_models
from urllib import parse
from data.helpers import getWhereClauses
import math
import csv
LOGIN_URL = '/login/'

@login_required(login_url=LOGIN_URL)
def data_per_aspect_topic(request, project_id):
    user = request.user
    page_size = int(request.GET.get("page-size", 10))
    page = int(request.GET.get("page", 1))
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    where_clause = [
        "dd.project_id = %s"
    ]
    query_args = []
    aspect_label = parse.unquote(request.GET.get("aspect-label", ""))
    topic_label = parse.unquote(request.GET.get("topic-label", ""))
    sentiment = request.GET.get("sentiment")
    sentiment_filter = ""
    if sentiment == "positive":
        sentiment_filter = "dd.sentiment > 0"
        where_clause.append(sentiment_filter)
    elif sentiment == "negative":
        sentiment_filter = "dd.sentiment < 0"
        where_clause.append(sentiment_filter)

    query_args.append(project_id)

    if aspect_label != "":
        where_clause.append('da."label" = %s')
        query_args.append(aspect_label)
    
    if topic_label != "":
        where_clause.append("da.topic = %s")
        query_args.append(topic_label)
    
    response_format = request.GET.get("format", "")
    
    with connection.cursor() as cursor:
        cursor.execute("""select count(*) from data_data dd inner join data_aspect da on dd.id = da.data_id inner join data_source ds on ds.id = dd.source_id where """ + getWhereClauses(request, where_clause),
                       query_args)

        row = cursor.fetchone()
    total = int(row[0])
    offset = (page - 1) * page_size
    total_pages = math.ceil(total / page_size)
    limit_offset_clause = ""

    if response_format == "":
        limit_offset_clause = """ limit %s offset %s;"""
        query_args.append(page_size)
        query_args.append(offset)
    query = """ select dd.date_created, dd."text" , ds."label" , dd.weighted_score , dd.sentiment , dd."language", dd.id from data_data dd inner join data_aspect da on dd.id = da.data_id inner join data_source ds on dd.source_id = ds.id where """ + getWhereClauses(request, where_clause) + """ order by dd.date_created desc """ + limit_offset_clause

    with connection.cursor() as cursor:
        cursor.execute(query,
                       query_args)
        rows = cursor.fetchall()

    
    if response_format == "csv":
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="data_items_per_aspect_topic.csv"'

        writer = csv.writer(response)
        writer.writerow(['Date', "Text", "Source", "Weighted", "Raw", "Language"])
        for row in rows:
            writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5]])
        return response

    if response_format == "word-cloud":
        with connection.cursor() as cursor:
            cursor.execute("""
                        WITH counts AS (
            SELECT keyword, ct::INT from data_data dd CROSS JOIN LATERAL each(keywords) AS k(keyword, ct) inner join data_aspect da on dd.id = da.data_id inner join data_source ds on dd.source_id = ds.id where """ + getWhereClauses(request, where_clause) + """ order by date_created desc """ + limit_offset_clause + ") SELECT keyword, SUM(ct)::INT keyword_count FROM counts GROUP BY keyword ORDER BY keyword_count desc limit 35", query_args)
            rows = cursor.fetchall()
            response = []
            for row in rows:
                response.append({
                    'keyword':row[0],
                    'keywordCount':row[1],
                })
            return JsonResponse(response, safe=False)
  
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