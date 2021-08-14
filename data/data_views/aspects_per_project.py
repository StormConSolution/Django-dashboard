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
        aspect_rules = project.aspect_model.aspectrule_set.all()
        for aspect in aspect_rules:
            aspects.append({
                'id': aspect.pk,
                'rule_name':aspect.rule_name,
            })
    return JsonResponse(aspects, safe=False)
