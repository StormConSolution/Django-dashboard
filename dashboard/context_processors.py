from django.conf import settings

from customize.models import Setting

def general_context(request):
    # See if we have a custom logo.
    try:
        custom_logo = Setting.objects.get(key='logo')
    except:
        custom_logo = ''

    return {
        'FLATFILE_URL': settings.FLATFILE_URL,
        'LANGUAGE_CODES':'|'.join([l[0] for l in settings.LANGUAGES]),
        'LANGUAGES':settings.LANGUAGES,
        'CUSTOM_LOGO':custom_logo,
    }
