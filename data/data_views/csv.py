from io import StringIO
import csv
import json
from datetime import date, datetime

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.base import ContentFile
from dashboard.tasks import process_data

from data import models


@method_decorator(csrf_exempt, name="upload_csv")
def csv_upload(request):
    try:
        project_id = request.GET.get("project-id")
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        date = datetime.now()
        file_name = date.strftime("%Y-%m-%d_%H:%M:%S_") + project_id + ".csv"
        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer)
        headers = []
        if request.GET.get("client", "") != "browser":
            body = body["data"]["validRows"]
        for element in body[0].keys():
            headers.append(element)
        csv_writer.writerow(headers)
        for element in body:
            row = []
            task_argument = {}
            task_argument["lang"] = 'en'
            task_argument["url"] = ''
            task_argument[""] = ''
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
                else:
                    task_argument["metadata"][value] = element[value]
                row.append(element[value])
            task_argument["text"] = element["text"]
            task_argument["project_id"] = project_id
            process_data.delay(task_argument)
            csv_writer.writerow(row)
    except Exception as e:
        print(e)
    default_storage.save(file_name, ContentFile(csv_buffer.getvalue().encode('utf-8')))
    return HttpResponse("csv upload")