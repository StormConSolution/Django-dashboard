from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404

import data.models as data_models
from data.helpers import getWhereClauses, getFiltersSQL


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def aspect_count(request, project_id):
    project = get_object_or_404(data_models.Project, pk=project_id)
    order_by = request.GET.get("order-by", "")
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied
    where_clauses = [
        "dd.project_id = %s"
    ]

    order_by_clause = 'count(da."label") desc'
    if order_by == "label":
        order_by_clause = 'da."label" asc'
    with connection.cursor() as cursor:
        cursor.execute("""
            select distinct da."label", count(da."label") from data_data dd inner join data_aspect da on dd.id = da.data_id inner join data_source ds on dd.source_id = ds.id where  """ + getWhereClauses(request, where_clauses) + """ group by da."label" order by """ + order_by_clause, [project.id])
        rows = cursor.fetchall()
    response = []
    for row in rows:
        aux = {}
        aux["aspectLabel"] = row[0]
        aux["aspectCount"] = row[1]
        response.append(aux)
    return JsonResponse(response, safe=False)
