import csv
import math
from urllib import parse

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

import data.models as data_models
from data.helpers import getWhereClauses
from data.serialize import serialize_rows


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def data_per_aspect_topic(request, project_id):
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

    if response_format == "word-cloud":
        with connection.cursor() as cursor:
            cursor.execute("""
                        WITH counts AS (
            SELECT keyword, ct::INT from data_data dd CROSS JOIN LATERAL each(keywords) AS k(keyword, ct) inner join data_aspect da on dd.id = da.data_id inner join data_source ds on dd.source_id = ds.id where """ + getWhereClauses(request, where_clause) + """ order by date_created desc """ + limit_offset_clause + ") SELECT keyword, SUM(ct)::INT keyword_count FROM counts GROUP BY keyword ORDER BY keyword_count desc limit 50", query_args)
            rows = cursor.fetchall()
            response = []
            for row in rows:
                response.append({
                    'keyword':row[0],
                    'keywordCount':row[1],
                })
            return JsonResponse(response, safe=False)
    
    with connection.cursor() as cursor:
        cursor.execute("""select count(*) from data_data dd inner join data_aspect da on dd.id = da.data_id inner join data_source ds on ds.id = dd.source_id where """ + getWhereClauses(request, where_clause),
                       query_args)

        row = cursor.fetchone()
    total_data = int(row[0])

    sql_query = """
    select dd.date_created, dd."text" , dd."url", ds."label"  , dd.sentiment , dd."language", dd.id
    from data_data dd inner join data_aspect da on dd.id = da.data_id inner join data_source ds on dd.source_id = ds.id
    where """ + getWhereClauses(request, where_clause) + """ order by dd.date_created desc """
    
    return serialize_rows(
        request,
        project_id,
        total_data,
        sql_query,
        where_clause,
        query_args,
        response_format,
        "data_items_per_aspect_topic.csv",
        extra_context={'topicLabel':topic_label, 'aspectLabel':aspect_label},
    )
