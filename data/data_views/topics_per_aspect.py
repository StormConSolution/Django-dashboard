from urllib import parse

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

import data.models as models
from data.helpers import getWhereClauses

@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def topics_per_aspect(request, project_id):
    this_project = get_object_or_404(models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied
    aspect_label = parse.unquote(request.GET.get("aspect-label", ""))
    max_topics = parse.unquote(request.GET.get("max-topics", 10))
    sentiment = request.GET.get("sentiment", "")

    where_clause = [
        'dd.project_id = %s',
        'da."label" = %s'
    ]

    if sentiment == "positive":
        where_clause.append("dd.sentiment > 0")
    elif sentiment == "negative":
        where_clause.append("dd.sentiment < 0")

    response = []
    with connection.cursor() as cursor:
        cursor.execute("""select da.topic , count(da.topic ) from data_aspect da inner join data_data dd on da.data_id = dd.id inner join data_source ds on ds.id = dd.source_id where """ + getWhereClauses(request, where_clause) + """ group by (da.topic) order by count(da.topic) desc limit %s""", [project_id, aspect_label, max_topics])
        rows = cursor.fetchall()
    for row in rows:
        response.append({
            'topicLabel':row[0],
            'topicCount':row[1],
        })
        
    return JsonResponse(response, safe=False)
