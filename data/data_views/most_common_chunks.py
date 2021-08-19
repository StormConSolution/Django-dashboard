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

def _similar_sentiment(x, y):
    """
    Check if both chunks have the same polarity.
    """
    return (x['positiveCount'] > x['negativeCount'] and y['positiveCount'] > y['negativeCount']) or\
           (x['positiveCount'] < x['negativeCount'] and y['positiveCount'] < y['negativeCount'])

def _obvious_sentiment(t):
    """
    Check if one sentiment or another is sufficiently dominant.
    """
    eps = 0.7
    pos = t['positiveCount']
    neg = t['negativeCount']
    total = t['total']
    return float(pos) / float(total) >= eps or float(neg) / float(total) > eps

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
                da.chunk,
                sum(case when da.sentiment > 0 then 1 else 0 end) as pos,
                sum(case when da.sentiment < 0 then 1 else 0 end) as neg 
            from 
                data_aspect da inner join data_data dd on dd.id = da.data_id inner join data_source ds on ds.id = dd.source_id
            where 
                da.chunk != '' and (da.sentiment > 0 or da.sentiment < 0) and {}
            group by 
                da.chunk
            order by count(lower(da.chunk)) desc limit {}""".format(where_clause, upper_limit), [project_id])
        rows = cursor.fetchall()
    
    temp_response = []

    for row in rows:
        if row[2] > 0 or row[3] > 0:
            temp_response.append({
                "total": row[0],
                "chunk": row[1].strip(string.punctuation),
                "positiveCount": row[2],
                "negativeCount": row[3],
            })

    # Before we return, collate chunks based on substring match. First sort by
    # length of chunk, smallest to largest.
    temp_response = sorted(temp_response, key = lambda i: len(i['chunk']), reverse=True)
    merged_chunks = []

    for idx, t in enumerate(temp_response):
        merged = False
        for other in merged_chunks:
            if t['chunk'].lower() in other['chunk'].lower() and _similar_sentiment(t, other):
                other['positiveCount'] += t['positiveCount']
                other['negativeCount'] += t['negativeCount']
                other['total'] += t['total']
                merged = True
                break

        if not merged:
            print("appending", t)
            merged_chunks.append(t)
    
    # Now remove any that are not valid, sort again by count and return that
    # final list.
    response = filter(lambda x: _obvious_sentiment(x), merged_chunks)
    response = sorted(response, key = lambda i: i['total'], reverse=True)

    return JsonResponse(response[:limit], safe=False)
