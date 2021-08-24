import csv
import math

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

import data.models as data_models
from data.helpers import get_where_clauses, get_order_by
from data.serialize import serialize_rows


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def data_per_classification(request, project_id):
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
            select count(dd.id) from data_classification dc inner join data_entity_classifications dec2 on dc.id = dec2.classification_id inner join data_data_entities dde ON dde.entity_id = dec2.entity_id inner join data_data dd on dd.id = dde.data_id inner join data_source ds on ds.id = dd.source_id where """ + get_where_clauses(request, where_clause), [project_id, classification_id])
        row = cursor.fetchone()
    total_data = int(row[0])

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

    if response_format == "word-cloud":
        with connection.cursor() as cursor:
            cursor.execute("""
                with counts as ( SELECT keyword, ct::int from data_data dd CROSS JOIN LATERAL jsonb_each_text(keywords) AS k(keyword, ct) inner join data_classification dc on dc.id=%s inner join data_entity_classifications dec2 on dc.id = dec2.classification_id inner join data_data_entities dde ON dde.entity_id = dec2.entity_id inner join data_source ds on ds.id = dd.source_id where dd.id= dde.data_id and """ + get_where_clauses(request, where_clause) + """order by date_created desc ) SELECT keyword, SUM(ct)::INT keyword_count FROM counts GROUP BY keyword ORDER BY keyword_count desc limit 50""" , query_args)
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
    
    where_clause = [
        "dd.project_id = %s",
        "dc.id = %s"
    ]
    
    if sentiment == "positive":
        where_clause.append("dd.sentiment > 0")
    if sentiment == "negative":
        where_clause.append("dd.sentiment < 0")
    if sentiment == "neutral":
        where_clause.append("dd.sentiment = 0")
    
    sql_query = """
    select distinct on (dd.date_created, dd.id) dd.date_created, dd."text", dd."url", ds."label" , dd.sentiment , dd."language", dd.id
    from data_classification dc inner join data_entity_classifications dec2 on dc.id = dec2.classification_id inner join data_data_entities dde ON dde.entity_id = dec2.entity_id inner join data_data dd on dd.id = dde.data_id inner join data_source ds on ds.id = dd.source_id
    where """ + get_where_clauses(request, where_clause) + get_order_by(request, "dd.date_created", "desc")
    
    return serialize_rows(
        request,
        project_id,
        total_data,
        sql_query,
        where_clause,
        query_args,
        response_format,
        "data_items.csv",
    )
