from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from data import models

@login_required
@csrf_exempt
def update_aspect_rule_weight(request, aspect_weight_id):
    new_weight = int(request.GET.get("weight", "1"))
    aspect_rule = models.AspectWeight.objects.get(id=aspect_weight_id)
    aspect_rule.weight = new_weight
    aspect_rule.save()
    return HttpResponse(status=200)
    
