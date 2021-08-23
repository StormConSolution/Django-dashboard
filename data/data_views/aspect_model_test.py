from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
import requests

import data.models as models

@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def aspect_model_test(request):

    text = request.POST.get("test-aspect-model-text", "")
    language = request.POST.get("text-language", "")
    aspect_model_id = request.POST.get("aspect-model")
    api_key = request.POST.get("api-key", "")
    aspect_model = models.AspectModel.objects.get(pk=aspect_model_id)

    req = requests.post("%s/v4/%s/aspect.json" % (settings.API_HOST, api_key), 
            data={"text": text, "lang": language, "model":aspect_model.label, "neutral":1})
    response = req.json()

    return JsonResponse(response, safe=False, status=req.status_code)
