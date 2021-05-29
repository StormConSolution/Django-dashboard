from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from data.helpers import getWhereClauses, getFiltersSQL
import csv
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.core.files import File
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.base import ContentFile
from io import StringIO



@method_decorator(csrf_exempt, name="upload_csv")
@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def csv_upload(request):
    project_id = request.GET.get("project-id")
    print("project id: ", project_id)
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    date = datetime.datetime.now()
    file_name = date.strftime("%Y-%m-%d_%H:%M:%S_") + project_id + ".csv"
    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer)
    for element in body:
        csv_writer.writerow([element["date"], element["text"], element["source"]])
    default_storage.save(file_name, ContentFile(csv_buffer.getvalue().encode('utf-8')))
    return HttpResponse("csv upload")