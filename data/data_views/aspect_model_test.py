import requests

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings

import data.models as models


import requests

import data.models as models

@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def aspect_model_test(request):

    text = request.POST.get("test-aspect-model-text", "")
    language = request.POST.get("language", "")
    aspect_model_id = request.POST.get("aspect-model")
    aspect_model = models.AspectModel.objects.get(pk=aspect_model_id)

    # Fetch the apikeys for this user and grab the first one.
    h = hmac.new(bytes(settings.HMAC_SECRET, 'utf8'), bytes(request.user.email, 'utf8'), 'sha256')
    hashkey = h.hexdigest()
    resp = requests.get("{}/credentials/fetch/{}/{}/".format(
        settings.AUTH_HOST,
        request.user.email,
        hashkey)).json()
    
    if len(resp['apikeys']) > 0:
        apikey = resp['apikeys'][0]
        req = requests.post("%s/v4/%s/aspect.json" % (settings.API_HOST, apikey), 
                data={"text": text, "lang": language, "model":aspect_model.label, "neutral":1})
        response = req.json()
        return JsonResponse(response, safe=False, status=req.status_code)
    else:
        return JsonResponse({'error':'No API key found'}, safe=False, status=400)
