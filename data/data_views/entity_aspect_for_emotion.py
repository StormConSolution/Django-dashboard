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
def entity_aspect_for_emotion(request, project_id):
    this_project = get_object_or_404(models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    if models.Entity.objects.filter(data__project_id=project_id).count()==0:
        return JsonResponse({}, safe=False)
    if models.Data.objects.filter(project_id=project_id).count() == 0:
        return JsonResponse({}, safe=False)
    if models.Aspect.objects.filter(data__project_id = project_id).count() == 0:
        return JsonResponse({}, safe=False)
    languages =parse.unquote(request.GET.get("languages", "")).split(",")
    sources = parse.unquote(request.GET.get("sourcesID", "")).split(",")
    function_arguments = ""
    if languages != ['']:
        languages = " ,languages := array['" + "'::character varying,'".join(languages) + "'::character varying] "
        function_arguments = languages

    if sources != ['']:
        sources = " ,source_ids := array["+ " ,".join(sources) + "] "
        function_arguments = function_arguments + sources
    with connection.cursor() as cursor:
        cursor.execute("""select * from get_entity_aspect_counts(13, %s """ + function_arguments + """ )where entity in (SELECT entity FROM get_entity_aspect_counts(13, %s """ + function_arguments + """) group by (entity, entity_count) ORDER BY entity_count desc limit 10) ORDER BY entity_count desc ;""", [project_id, project_id])
        rows = cursor.fetchall()
    
    response = []
    for row in rows:
        response.append({"entityLabel": row[0], "entityCount": row[1], "aspectLabel": row[2], "aspectCount": row[3]})
        
    return JsonResponse(response, safe=False)
