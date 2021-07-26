from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.conf import settings
from django.http import JsonResponse
from django.db import connection

from data import models


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def metadata_keys(request, project_id):

    metadata_key = request.GET.get("metadata-key", "")

    if metadata_key == "":
        with connection.cursor() as cursor:
            cursor.execute("""select distinct (jsonb_object_keys(dd.metadata)) 
            from data_data as dd where  dd.project_id = %s""", [project_id])
            rows = cursor.fetchall()
        response = {
            'data':{
                'metadata-keys': []
            }
        }
        for elem in rows:
            response["data"]["metadata-keys"].append(elem[0])

        return JsonResponse(response)
    with connection.cursor() as cursor:
        cursor.execute("""SELECT distinct(dd.metadata ->> %s) 
        FROM data_data dd where dd.project_id = %s;
        """, [metadata_key, project_id])
        rows = cursor.fetchall()
    
    response = {
        'data':{
            'metadata-key': metadata_key,
            'metadata-values': [],
        }
    }

    for elem in rows:
        response["data"]["metadata-values"].append(elem[0]) 

    return JsonResponse(response)