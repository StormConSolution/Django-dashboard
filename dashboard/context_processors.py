from django.conf import settings

from customize.models import Setting
from data import models as data_models
from data import helpers as data_helpers

def general_context(request):
    """
    Fetch various site-wide data we need to render.
    """
    # See if we have a custom logo.
    try:
        custom_logo = Setting.objects.get(key='logo', users=request.user)
    except:
        custom_logo = ''
    guest_user = request.user.username == "guest@repustate.com"
    
    if request.user.is_authenticated:
        custom_aspects = data_models.AspectModel.objects.filter(users=request.user).values('id', 'label', 'language')
        # Fetch my apikeys.
        try:
            apikeys = data_helpers.get_api_keys(request.user)['apikeys']
        except Exception as e:
            apikeys = []
    else:
        custom_aspects = []
        apikeys = []
    
    return {
        'API_HOST': settings.API_HOST,
        'APIKEYS': apikeys,
        'FLATFILE_URL': settings.FLATFILE_URL,
        'LANGUAGE_CODES':'|'.join([l[0] for l in settings.LANGUAGES]),
        'CUSTOM_LOGO':custom_logo,
        'UPLOAD_CSV_FROM_CLIENT': settings.UPLOAD_CSV_FROM_CLIENT,
        'GUEST_USER': guest_user,
        "CUSTOM_ASPECT_MODELS": custom_aspects,
        'STANDARD_ASPECT_MODELS': data_models.AspectModel.objects.filter(standard=True).values('id', 'label'),
    }
