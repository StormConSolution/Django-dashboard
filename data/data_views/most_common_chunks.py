import re
import string

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

import data.models as data_models
from data.helpers import get_where_clauses

@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def most_common_chunks(request, project_id):
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    where_clause = get_where_clauses(request, [
        "dd.project_id = %s"
    ])

    try:
        # This just guards against SQL injection since we're sloppily appending
        # the limit to the query string. 
        limit = int(request.GET['limit'])
    except:
        # Not a valid integer.
        limit = 15
    
    # We multiply by 3 to get more results than we actually need just in case we
    # collate a few because of # similarity.
    upper_limit = limit * 3

    with connection.cursor() as cursor:
        cursor.execute("""
            select 
                count(*),
                lower(da.chunk),
                sum(case when da.sentiment > 0 then 1 else 0 end) as pos,
                sum(case when da.sentiment < 0 then 1 else 0 end) as neg 
            from 
                data_aspect da inner join data_data dd on dd.id = da.data_id inner join data_source ds on ds.id = dd.source_id
            where 
                da.chunk != ''  and (dd.sentiment > 0 or dd.sentiment < 0) and {}
            group by 
                lower(da.chunk) order by count(lower(da.chunk)) desc limit {}""".format(where_clause, upper_limit), [project_id])
        rows = cursor.fetchall()
    
    temp_response = []

    for row in rows:
        if row[2] > 0 or row[3] > 0:
            temp_response.append({
                "total": row[0],
                "chunk": re.sub(r'\bi\b', 'I', row[1].strip(string.punctuation)),
                "positiveCount": row[2],
                "negativeCount": row[3],
                "valid":True,
            })

    # Before we return, collate chunks based on substring match. First sort by
    # length of chunk, smalles to largest.
    temp_response = sorted(temp_response, key = lambda i: len(i['chunk']))
    for idx, t in enumerate(temp_response):
        for next_one in temp_response[idx+1:]:
            if next_one['valid'] and t['valid'] and next_one['chunk'].find(t['chunk']) >= 0:
                next_one['positiveCount'] += t['positiveCount']
                next_one['negativeCount'] += t['negativeCount']
                next_one['total'] += t['total']
                t['valid'] = False
    
    # Now remove any that are not valid, sort again by count and return that final list.
    response = list(filter(lambda x: x['valid'], temp_response))
    response = sorted(response, key = lambda i: i['total'])
    response.reverse()

    return JsonResponse(response[:limit], safe=False)
