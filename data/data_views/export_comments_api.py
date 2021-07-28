from data.data_views.export_comments import export_comments
import json
import requests

from exportcomments import ExportComments
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from data import models

from data import export_comments
from dashboard.tasks import process_data
@csrf_exempt
def export_comments_api(request):
    body_unicode = request.body.decode('utf-8')
    export_request = json.loads(body_unicode)
    guid = export_request["guid"]
    project = models.Project.objects.get(exportcomments__guid=guid)
    source = models.Source.objects.get(exportcomments__guid=guid)
    ex = ExportComments(settings.EXPORTCOMMENTS_API_KEY)
    export = ex.exports.check(guid).body
    export_url = export["data"][0]["rawUrl"]
    func = export_comments.get_function(source.label)
    response = requests.get('https://www.exportcomments.com' + export_url).json()
    task_arguments = func(response, project.id, source.label)
    for task_argument in task_arguments:
        process_data.delay(task_argument)
    return HttpResponse(status=200)
