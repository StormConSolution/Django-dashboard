import hmac

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import requests

@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def sentiment_test(request):

    text = request.POST.get("test-sentiment-text", "")
    language = request.POST.get("language", "")
    api_key = request.POST.get("api-key", "")

    req = requests.post("%s/v4/%s/score.json" % (settings.API_HOST, api_key),
        data={"text": text, "lang": language})
    response = req.json()
    return JsonResponse(response, safe=False, status=req.status_code)


