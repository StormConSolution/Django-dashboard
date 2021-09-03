import csv
import math

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from data.helpers import get_where_clauses, get_order_by
import data.models as data_models

from data.serialize import serialize_rows
@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def data_per_classification_and_entity(request, project_id):
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

    aspect_label = request.GET.get("aspect-label", "")
    aspect_inner_join = ""
    if aspect_label != "":
        where_clause.append('da."label" = %s')
        aspect_inner_join = "inner join data_aspect da on da.data_id = dd.id"
        query_args.append(aspect_label)

    with connection.cursor() as cursor:
        cursor.execute("""
        select count(*) from data_data dd inner join data_data_entities dde on dd.id = dde.data_id inner join data_entity de on dde.entity_id = de.id inner join data_entity_classifications dec2 on de.id = dec2.entity_id inner join data_classification dc on dec2.classification_id = dc.id inner join data_source ds on dd.source_id = ds.id """ + aspect_inner_join + """ where """ + get_where_clauses(request, where_clause),
                       query_args)
        row = cursor.fetchone()
    total_data = int(row[0])

    response_format = request.GET.get("format", "")

    if response_format == "word-cloud":
        with connection.cursor() as cursor:
            cursor.execute("""
            WITH counts AS (
            SELECT keyword, ct::INT from data_data dd CROSS JOIN LATERAL jsonb_each_text(keywords) AS k(keyword, ct) inner join data_data_entities dde on dd.id = dde.data_id inner join data_entity de on dde.entity_id = de.id inner join data_entity_classifications dec2 on de.id = dec2.entity_id inner join data_classification dc on dec2.classification_id = dc.id inner join data_source ds on dd.source_id = ds.id """ + aspect_inner_join + """  where """ + get_where_clauses(request, where_clause) + """ order by date_created desc ) SELECT keyword, SUM(ct)::INT keyword_count FROM counts GROUP BY keyword ORDER BY keyword_count desc limit 50""", query_args)
            rows = cursor.fetchall()
            response = []
            for row in rows:
                response.append({
                    'keyword':row[0],
                    'keywordCount':row[1],
                })
            return JsonResponse(response, safe=False)

    sql_query = """
        select dd.date_created, dd."text" , dd."url", ds."label"  , dd.sentiment , dd."language", dd.id
        from data_data dd inner join data_data_entities dde on dd.id = dde.data_id inner join data_entity de on dde.entity_id = de.id inner join data_entity_classifications dec2 on de.id = dec2.entity_id inner join data_classification dc on dec2.classification_id = dc.id inner join data_source ds on dd.source_id = ds.id """+ aspect_inner_join+""" where """ + get_where_clauses(request, where_clause) + get_order_by(request, "dd.date_created", "desc") 

    extra_context = {
        "entity":entity,
        "classification":classification
    }
    
    return serialize_rows(
        request,
        project_id,
        total_data,
        sql_query,
        where_clause,
        query_args,
        response_format,
        "data_items.csv",
        **extra_context
    )
