from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from data.helpers import get_api_key


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def get_user_api_keys(request):
    return JsonResponse(get_api_key(request.user), safe=False)