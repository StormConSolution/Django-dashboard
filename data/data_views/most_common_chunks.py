from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

import data.models as data_models
from data.helpers import getWhereClauses

@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def most_common_chunks(request, project_id):
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    where_clause = [
        "dd.project_id = %s"
    ]

    with connection.cursor() as cursor:
        cursor.execute("""
            select count(*), lower(da.chunk), sum(case when dd.sentiment > 0 then 1 else 0 end) as pos, sum(case when dd.sentiment < 0 then 1 else 0 end) as neg from data_aspect da inner join data_data dd on dd.id = da.data_id inner join data_source ds on ds.id = dd.source_id where da.chunk != ''  and (dd.sentiment > 0 or dd.sentiment < 0) and """ + getWhereClauses(request, where_clause) + """ group by lower(da.chunk) order by count(lower(da.chunk)) desc limit 20""", [project_id])
        rows = cursor.fetchall()
    response = []
    for row in rows:
        response.append({
            "chunk": row[1],
            "positiveCount": row[2],
            "negativeCount": row[3],
        })
    return JsonResponse(response, safe=False)
