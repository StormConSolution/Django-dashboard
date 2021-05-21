from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from data.helpers import getWhereClauses
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse
import data.models as models
from urllib import parse
from data.helpers import getWhereClauses
import requests
from django.conf import settings
import json

LOGIN_URL = '/login/'

@login_required(login_url=LOGIN_URL)
def aspect_model_test(request):

    text = request.POST.get("test-aspect-model-text", "")
    language = request.POST.get("language", "")
    aspect_model_id = request.POST.get("aspect-model")
    aspect_model = models.AspectModel.objects.get(pk=aspect_model_id)

    req = requests.post("%s/v4/%s/aspect.json" % (settings.API_HOST, settings.APIKEY), data={"text": text, "lang": language, "model":aspect_model.label}, params={"text": "food is good", "lang": "en", "model":"hotel"})
    response = json.loads(req.text)
    return JsonResponse(response, safe=False, status=req.status_code)