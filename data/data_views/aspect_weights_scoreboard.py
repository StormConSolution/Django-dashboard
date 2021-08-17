from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

import data.models as data_models


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def aspect_weights_scoreboard(request, project_id):
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied
    
    total_data_aspects = data_models.Aspect.objects.filter(
        data__project=project,
        sentiment__gt=0).count()

    response = {
        'data': {
            'total_aspects_data': total_data_aspects,
            'aspect_weights': [],
            'max_score':0,
        },
    }
    
    if project.aspect_model is not None:
        aspect_rules = project.aspect_model.aspectrule_set.all()
        for aspect_rule in aspect_rules:
            try:
                total_positives = data_models.Aspect.objects.filter(sentiment__gt=0, label=aspect_rule.rule_name,
                                                                    data__project=project).count()
                total_aspect_data = data_models.Aspect.objects.filter(label=aspect_rule.rule_name,
                                                                      data__project=project).count()
                aspect_weight = aspect_rule.aspectweight_set.get(project=project)
                if aspect_weight:
                    response["data"]["aspect_weights"].append({
                        'id': aspect_weight.id,
                        'rule_name': aspect_rule.rule_name,
                        'total_positives': total_positives,
                        'total_aspect_data': total_aspect_data,
                        'weight': aspect_weight.weight,
                    })
                    response["data"]["max_score"] += aspect_weight.weight
            except:
                pass
    
    return JsonResponse(response, safe=False)
