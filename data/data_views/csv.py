from io import StringIO
import csv
import json
import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.base import ContentFile



@method_decorator(csrf_exempt, name="upload_csv")
def csv_upload(request):
    project_id = request.GET.get("project-id")
    print("project id: ", project_id)
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    date = datetime.datetime.now()
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
        for value in element:
            row.append(element[value])
        csv_writer.writerow(row)
    default_storage.save(file_name, ContentFile(csv_buffer.getvalue().encode('utf-8')))
    return HttpResponse("csv upload")