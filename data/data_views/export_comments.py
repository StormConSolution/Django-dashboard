from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.shortcuts import redirect
from exportcomments import ExportComments

from data import models as data_models
from data.export_comments import get_source


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def export_comments(request):
    """
    Register a request to fetch comments from a supported service.
    """
    url = request.POST.get("export-comments-url", "")
    project_id = request.POST.get("project-id", "")

    if not url or not project_id:
        messages.add_message(request, messages.ERROR, 'URL and project ID are required')
        return redirect("project")

    project = data_models.Project.objects.get(pk=project_id)
    
    source = get_source(url)
    if not source:
        messages.add_message(request, messages.ERROR,
                             'Fetch only supports YouTube, Twitter, Instagram, TikTok and Vimeo')
        return redirect("project", project_id)

    ex = ExportComments(settings.EXPORTCOMMENTS_API_KEY)
    exportcomments_response = ex.exports.create(
        url=url, replies='false', twitterType='Tweets'
    )
    
    try:
        guid = exportcomments_response.body["data"]["guid"]
        export_comment = data_models.ExportComments.objects.create(
            project=project,
            source=source[0],
            url=url,
            guid=exportcomments_response.body["data"]["guid"],
            status=data_models.RUNNING,
        )
    except KeyError:
        # The export wasn't created properly. Put this in a queue to process
        # later.
        export_comment = data_models.ExportComments.objects.create(
            project=project,
            source=source[0],
            url=url,
            guid=exportcomments_response.body["data"]["guid"],
            status=data_models.QUEUED
        )

    return redirect("project", project_id)
