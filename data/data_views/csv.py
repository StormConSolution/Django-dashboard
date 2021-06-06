import csv
import json

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from dashboard.tasks import process_data

@method_decorator(csrf_exempt, name="upload_csv")
def csv_upload(request):
    try:
        project_id = request.GET.get("project-id")
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        if request.GET.get("client", "") != "browser":
            body = body["data"]["validRows"]
        
        for element in body:
            task_argument = {
                "project_id": project_id,
                "lang":'en',
                "url":'',
                "source":'',
                "metadata":{},
            }
            
            for key in ('lang', 'date', 'source', 'url', 'text'):
                if key in element:
                    task_argument[key] = element[key]
            
            if "$custom" in element.keys():
                task_argument["metadata"] = element["$custom"]
            

            process_data.delay(task_argument)

    except Exception as e:
        return HttpResponseBadRequest("error in file upload: {}".format(e))
    
    return HttpResponse("OK")
