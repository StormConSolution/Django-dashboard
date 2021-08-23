import json

from django.conf import settings
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from exportcomments import ExportComments
import requests

from data import models as data_models
from data.data_views.export_comments import export_comments
from data import export_comments
from dashboard.tasks import process_data

@csrf_exempt
def export_comments_api(request):
    """
    Webhook endpoint for exportcomments.

    Fetch the results of an export comments API call and push each item into
    our celery queue.
    """
    body_unicode = request.body.decode('utf-8')
    export_request = json.loads(body_unicode)
    guid = export_request["guid"]
    if export_request["status"] == "done":
        project = data_models.Project.objects.get(exportcomments__guid=guid)
        source = data_models.Source.objects.get(exportcomments__guid=guid)
        export_comment = data_models.ExportComments.objects.get(guid=guid)
        export_comment.status = data_models.DONE
        export_comment.save()


        ex = ExportComments(settings.EXPORTCOMMENTS_API_KEY)
        export = ex.exports.check(guid).body
        export_url = export["data"][0]["rawUrl"]

        func = export_comments.get_function(source.label)
        response = requests.get('https://www.exportcomments.com' + export_url).json()
        task_arguments = func(response, project.id, source.label)
        for task_argument in task_arguments:
            process_data.delay(task_argument)
    elif export_request["status"] == "error":
        export_comment = data_models.objects.get(guid=guid)
        export_comment.status = data_models.ExportComments.ERROR
        export_comment.save()

    return HttpResponse(status=200)
