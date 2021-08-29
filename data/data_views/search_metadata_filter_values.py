from urllib import parse

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import JsonResponse


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def search_metadata_filter_values(request, project_id):
    metadata_filter_key = parse.unquote(request.GET.get("metadata-filter-key", ""))
    metadata_filter_value = parse.unquote(request.GET.get("metadata-filter-value", ""))
    metadata_filter_value = '%' + metadata_filter_value + '%'

    response = {'data': {
        'values': []
    }}
    with connection.cursor() as cursor:
        cursor.execute(
            "select dd.metadata->>%s from data_data dd where dd.project_id = %s and dd.metadata->>%s like %s order by dd.date_created desc limit 200",
        [metadata_filter_key, project_id, metadata_filter_key, metadata_filter_value])
        rows = cursor.fetchall()

        for row in rows:
            response["data"]["values"].append(row[0])

    return JsonResponse(response, safe=False)
