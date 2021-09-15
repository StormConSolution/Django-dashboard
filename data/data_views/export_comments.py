import logging
log = logging.getLogger()
import uuid

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
        messages.error(request, 'URL and project ID are required')
        return redirect("project")

    project = data_models.Project.objects.get(pk=project_id)
    
    source = get_source(url)
    if not source:
        messages.error(request, 'Unsupported source URL: {}'.format(url))
        return redirect("project", project_id)

    ex = ExportComments(settings.EXPORTCOMMENTS_API_KEY)
    ex_response = ex.exports.create(
        url=url, replies='false', twitterType='Tweets'
    )
    
    # Request ID to keep these logs together.
    params = {
        "request_id": str(uuid.uuid4())
    }
    
    log.info("Exportcomments request made",
            extra={'url':url, 'body':ex_response.body, 'project_id':project_id, **params})
    
    try:
        guid = ex_response.body["data"]["guid"]
        export_comment = data_models.ExportComments.objects.create(
            project=project,
            source=source[0],
            url=url,
            guid=guid,
            status=data_models.RUNNING,
        )
    except KeyError:
        # The export wasn't created properly. Put this in a queue to process
        # later.
        export_comment = data_models.ExportComments.objects.create(
            project=project,
            source=source[0],
            url=url,
            guid='',
            status=data_models.QUEUED
        )
        log.error("Error in requesting exportcomments fetch", extra={**params})

    return redirect("project", project_id)
