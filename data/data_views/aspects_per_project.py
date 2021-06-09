from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

import data.models as data_models

@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def aspects_per_project(request, project_id):
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied
    
    aspects = []
    if project.aspect_model is not None:
        aspects = list(project.aspect_model.aspectrule_set.values_list('rule_name', flat=True))

    return JsonResponse(aspects, safe=False)
