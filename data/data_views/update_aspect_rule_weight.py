import csv
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from dashboard.tasks import process_data, job_complete

from data import models

@login_required
@csrf_exempt
def update_aspect_rule_weight(request, aspect_weight_id):
    new_weight = int(request.GET.get("weight","1"))
    aspect_rule = models.AspectWeight.objects.get(id=aspect_weight_id)
    aspect_rule.weight = new_weight
    aspect_rule.save()
    return HttpResponse(status=200)
    
