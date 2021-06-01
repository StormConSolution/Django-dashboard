from django.conf import settings

def general_context(request):
    return {
        'FLATFILE_URL': settings.FLATFILE_URL,
        'LANGUAGE_CODES':'|'.join([l[0] for l in settings.LANGUAGES]),
    }
