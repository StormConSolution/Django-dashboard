from exportcomments import ExportComments

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from data import models
from data.export_comments import get_source
@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def export_comments(request):
    url = request.POST.get("export-comments-url","")
    project_id = request.POST.get("project-id","")
    ex = ExportComments(settings.EXPORTCOMMENTS_API_KEY)
    exportcomments_response = ex.exports.create(
        url=url, replies='false', twitterType='Tweets'
    )

    source = get_source(url)
    if not source:
        messages.add_message(request, messages.ERROR, 'Fetch only supports Twitter, Facebook, Instagram and YouTube')
        return redirect("project", project_id)
    project = models.Project.objects.get(pk=project_id)
    export_comment = models.ExportComments(
        project=project,source=source[0], guid=exportcomments_response.body["data"]["guid"])
    export_comment.save()
    return redirect("project", project_id)