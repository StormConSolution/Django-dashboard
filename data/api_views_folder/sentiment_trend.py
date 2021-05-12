from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from data.helpers import getWhereClauses
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse, HttpResponse
import data.models as data_models
from urllib import parse
from data.helpers import getWhereClauses, getFiltersSQL
import math
import csv
LOGIN_URL = '/login/'

@login_required(login_url=LOGIN_URL)
def sentiment_trend(request, project_id):
    user = request.user
    page_size = int(request.GET.get("page-size", 10))
    page = int(request.GET.get("page", 1))
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    where_clause = []
    dateFrom = request.GET.get("date-from")
    dateTo = request.GET.get("date-to")
    languages = request.GET.get("languages").split(",")
    sources = parse.unquote(request.GET.get("sourcesID")).split(",")
    default = request.GET.get("default", "0")
    limit_clause = ""
    if default == "0":
        if not dateFrom:
            dateFrom = ""
        if not dateTo:
            dateTo = ""
        if dateFrom != "":
            where_clause.append("dd.date_created > '" + dateFrom + "'")
        if dateTo != "":
            where_clause.append("dd.date_created < '" + dateTo + "'")
    else:
        limit_clause = "limit 3"
    map(lambda x: "''%s''" % x, sources)
    map(lambda x: "''%s''" % x, languages)
    where_clause.append("dd.language in (%s)" % ("'" + "','".join(languages) + "'"))
    where_clause.append('ds."id" in (%s)' % ("'" + "','".join(sources) + "'"))
    
    where_clause.append("dd.project_id = %s")

    with connection.cursor() as cursor:
        cursor.execute("""
            select dates.date, sum(case when dd.sentiment > 0 then 1 else 0 end) as positives , sum(case when dd.sentiment < 0 then 1 else 0 end) as negatives from (select distinct(to_char (dd.date_created, 'YYYY-MM')) as date from data_data dd inner join data_source ds on ds.id=dd.source_id where """ + " and ".join(where_clause) + """ order by date desc """ + limit_clause + """ ) as dates inner join data_data dd on to_char (dd.date_created, 'YYYY-MM') = dates.date inner join data_source ds on ds.id = dd.source_id where """ + " and ".join(where_clause) + """ group by dates.date order by dates.date asc;""", [project.id, project_id])
        rows = cursor.fetchall()
    
    response=[]
    for row in rows:
        response.append({
            "date": row[0],
            "positivesCount": row[1],
            "negativesCount": row[2]
        })


    return JsonResponse(response, safe=False)