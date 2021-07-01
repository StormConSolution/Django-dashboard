from django.conf import settings

from customize.models import Setting

def general_context(request):
    # See if we have a custom logo.
    try:
        custom_logo = Setting.objects.get(key='logo', users=request.user)
    except:
        custom_logo = ''
    guest_user = request.user.username == "guest@repustate.com"
    firebase_auth = settings.FIREBASE_AUTH == "1"
    return {
        'FLATFILE_URL': settings.FLATFILE_URL,
        'LANGUAGE_CODES':'|'.join([l[0] for l in settings.LANGUAGES]),
        'CUSTOM_LOGO':custom_logo,
        'UPLOAD_CSV_FROM_CLIENT': settings.UPLOAD_CSV_FROM_CLIENT,
        'GUEST_USER': guest_user,
        'FIREBASE_AUTH': firebase_auth,
    }
