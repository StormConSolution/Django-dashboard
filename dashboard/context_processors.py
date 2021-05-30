from django.conf import settings

def general_context(request):
    return {'FLATFILE_URL': settings.FLATFILE_URL}