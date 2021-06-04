from io import StringIO
import csv
import json
from datetime import datetime

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.base import ContentFile
from dashboard.tasks import process_data

@method_decorator(csrf_exempt, name="upload_csv")
def csv_upload(request):
    try:
        defined_fields = ["lang", "date", "source", "url", "text"]
        project_id = request.GET.get("project-id")
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        if request.GET.get("client", "") != "browser":
            body = body["data"]["validRows"]
        print(body)
        for element in body:
            task_argument = {}
            task_argument["lang"] = 'en'
            task_argument["url"] = ''
            task_argument["source"] = ''
            task_argument["metadata"] = {}
            for value in element:
                if value == "lang":
                    task_argument[value] = element[value]
                elif value == "date":
                    task_argument[value] = element[value]
                elif value == "source":
                    task_argument[value] = element[value]
                elif value == "url":
                    task_argument[value] = element[value]
            if "$custom" in element.keys():
                    task_argument["metadata"] = element["$custom"]
            task_argument["text"] = element["text"]
            task_argument["project_id"] = project_id
            process_data.delay(task_argument)
    except Exception as e:
        print(e)
    return HttpResponse("csv upload")