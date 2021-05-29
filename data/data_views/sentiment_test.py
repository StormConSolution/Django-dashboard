import hmac

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import requests

@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def sentiment_test(request):

    text = request.POST.get("test-sentiment-text", "")
    language = request.POST.get("language", "")
    
    h = hmac.new(bytes(settings.HMAC_SECRET, 'utf8'), bytes(request.user.email, 'utf8'), 'sha256')
    hashkey = h.hexdigest()
    resp = requests.get("{}/credentials/fetch/{}/{}/".format(
        settings.AUTH_HOST,
        request.user.email,
        hashkey)).json()
    
    if len(resp['apikeys']) > 0:
        apikey = resp['apikeys'][0]
        req = requests.post("%s/v4/%s/score.json" % (settings.API_HOST, apikey),
            data={"text": text, "lang": language})
        response = req.json()
        return JsonResponse(response, safe=False, status=req.status_code)
    else:
        return JsonResponse({'error':'No API key found'}, safe=False, status=400)

