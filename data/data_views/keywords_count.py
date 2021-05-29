from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

import data.models as models

@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def keywords_count(request, project_id):
    this_project = get_object_or_404(models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    response = []
    with connection.cursor() as cursor:
        cursor.execute("""select * from get_keyword_counts(%s) limit 20""", [project_id])
        rows = cursor.fetchall()
    for row in rows:
        response.append({
            'keyword':row[0],
            'keywordCount':row[1],
        })
        
    return JsonResponse(response, safe=False)
