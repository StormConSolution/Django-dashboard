from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from data.helpers import getWhereClauses
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse
import data.models as models
from urllib import parse
from data.helpers import getWhereClauses

LOGIN_URL = '/login/'

@login_required(login_url=LOGIN_URL)
def entity_aspect_for_emotion(request, project_id):
    this_project = get_object_or_404(models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    languages =parse.unquote(request.GET.get("languages", "")).split(",")
    sources = parse.unquote(request.GET.get("sources", "")).split(",")
    function_arguments = ""
    if languages != ['']:
        languages = " ,languages := array['" + "','".join(languages) + "'] "
        function_arguments = languages

    if sources != ['']:
        sources = " ,sources := array['" + "','".join(sources) + "'] "
        function_arguments = function_arguments + sources
    response = []
    with connection.cursor() as cursor:
        cursor.execute("""select * from get_entity_aspect_counts(13, %s """ + function_arguments + """ )where entity in (SELECT entity FROM get_entity_aspect_counts(13, %s """ + function_arguments + """) group by (entity, entity_count) ORDER BY entity_count desc limit 10) ORDER BY entity_count desc ;""", [project_id, project_id])
        rows = cursor.fetchall()
    
    for row in rows:
        response.append({"entityLabel": row[0], "entityCount": row[1], "aspectLabel": row[2], "aspectCount": row[3]})
        
    return JsonResponse(response, safe=False)