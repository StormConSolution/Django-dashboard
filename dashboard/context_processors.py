from django.conf import settings

from customize.models import Setting
from data import models as data_models

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
        custom_aspects = data_models.AspectModel.objects.filter(users=request.user).values('id', 'label')
    else:
        custom_aspects = []
    
    return {
        'API_HOST': settings.API_HOST,
        'FLATFILE_URL': settings.FLATFILE_URL,
        'LANGUAGE_CODES':'|'.join([l[0] for l in settings.LANGUAGES]),
        'CUSTOM_LOGO':custom_logo,
        'UPLOAD_CSV_FROM_CLIENT': settings.UPLOAD_CSV_FROM_CLIENT,
        'GUEST_USER': guest_user,
        "CUSTOM_ASPECT_MODELS": custom_aspects,
        'STANDARD_ASPECT_MODELS': data_models.AspectModel.objects.filter(standard=True).values('id', 'label'),
        'FIREBASE_AUTH': settings.FIREBASE_AUTH,
        'FIREBASE_API_KEY':settings.FIREBASE_API_KEY,
        'FIREBASE_AUTH_DOMAIN':settings.FIREBASE_AUTH_DOMAIN,
        'FIREBASE_PROJECT_ID':settings.FIREBASE_PROJECT_ID,
        'FIREBASE_STORAGE_BUKCET':settings.FIREBASE_STORAGE_BUKCET,
        'FIREBASE_MESSAGING_SENDER_ID':settings.FIREBASE_MESSAGING_SENDER_ID,
        'FIREBASE_APP_ID':settings.FIREBASE_APP_ID,
    }
