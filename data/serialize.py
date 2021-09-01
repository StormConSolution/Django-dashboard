import codecs
import csv
import math

from django.db import connection
from django.http import JsonResponse, HttpResponse

def serialize_rows(
        request,
        project_id,
        total_data,
        sql_query,
        where_clause,
        query_args,
        response_format,
        filename,
        **extra_context):

    if extra_context.get("return_all_ids", False):
        response = {'data': {
            'ids': []
        }}
        with connection.cursor() as cursor:
            cursor.execute(sql_query, query_args)
            rows = cursor.fetchall()
            for row in rows:
                response["data"]["ids"].append(row[6])
            return JsonResponse(response, safe=False)

    page_size = int(request.GET.get("page_size", 10))
    page = int(request.GET.get("page", 1))
    offset = (page - 1) * page_size
    total_pages = math.ceil(total_data / page_size)

    limit_offset_clause = ""
    if response_format == "":
        limit_offset_clause = """ limit %s offset %s;"""
        query_args.append(page_size)
        query_args.append(offset)

    with connection.cursor() as cursor:
        cursor.execute(sql_query + limit_offset_clause, query_args)
        rows = cursor.fetchall()

        if response_format == "csv":
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
            response.write(codecs.BOM_UTF8)

            writer = csv.writer(response)
            writer.writerow(['Date', "Text", "URL", "Source", "Sentiment", "Language"])
            for row in rows:
                writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5]])
            return response

        response = {}
        response["data"] = []
        response["currentPage"] = page
        response["total"] = total_data
        response["totalPages"] = total_pages
        response["pageSize"] = page_size
        response.update(extra_context)

        for row in rows:
            response["data"].append({
                "dateCreated": row[0],
                "text": row[1],
                "url": row[2],
                "sourceLabel": row[3],
                "sentimentValue": row[4],
                "languageCode": row[5],
                "id": row[6]
            })

        return JsonResponse(response, safe=False)
