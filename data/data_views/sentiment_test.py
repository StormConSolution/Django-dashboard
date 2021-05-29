import json
from urllib import parse

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import requests

import data.models as models
from data.helpers import getWhereClauses
from data.helpers import getWhereClauses



@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def sentiment_test(request):

    text = request.POST.get("test-sentiment-text", "")
    language = request.POST.get("language", "")

    req = requests.post("%s/v4/%s/score.json" % (settings.API_HOST, settings.APIKEY), data={"text": text, "lang": language})
    response = json.loads(req.text)
    return JsonResponse(response, safe=False, status=req.status_code)
