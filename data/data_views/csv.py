import csv
import json
import uuid

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from data import models as data_models
from dashboard.tasks import process_data, job_complete

@method_decorator(csrf_exempt, name="upload_csv")
def csv_upload(request):

    try:
        project_id = request.GET.get("project-id")
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        original_body = body

        if request.GET.get("client", "") != "browser":
            number_of_rows = body['data']['meta']['length']
            guid = body['event']['id']
            body = body["data"]["validRows"]
        else:
            number_of_rows = len(body)
            guid = uuid.uuid4()

        data_models.ExportComments.objects.create(
            project_id=project_id,
            source=data_models.Source.objects.get(label='Upload'),
            url='',
            guid=guid,
            status=data_models.RUNNING,
            total=number_of_rows,
        )
        
        for element in body:
            task_argument = {
                "project_id": project_id,
                "lang":'',
                "source":'',
                "metadata":{},
            }
            
            for key in ('lang', 'date', 'source', 'url', 'text'):
                if key in element:
                    task_argument[key] = element[key]
            
            if "$custom" in element.keys():
                task_argument["metadata"] = element["$custom"]
            
            process_data.delay(task_argument)

        # Check if we need to send the completion task that fires off notifications.
        if 'event' in original_body:
            seq = original_body['event']['sequence']
            if seq['length'] - 1 == seq['index']:
                # This is the last page of results.
                job_complete.delay(guid)

    except Exception as e:
        return HttpResponseBadRequest("error in file upload: {}".format(e))
    
    return HttpResponse("OK")
