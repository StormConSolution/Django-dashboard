from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

import data.models as data_models
from data.helpers import get_where_clauses

@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def classification_by_sentiment(request, project_id):
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    where_clause = [
        'dd.project_id = %s',
    ]
    
    response = []
    
    limit = request.GET.get("limit", "5")
    
    with connection.cursor() as cursor:
        cursor.execute("""select dc.id, dc."label", count(dde.entity_id), sum(case when dd.sentiment > 0 then 1 else 0 end) as PosCount, sum(case when dd.sentiment < 0 then 1 else 0 end) as NegCount, sum(case when dd.sentiment = 0 then 1 else 0 end) as NeutCount from data_classification dc inner join data_entity_classifications dec2 on dc.id = dec2.classification_id inner join data_data_entities dde ON dde.entity_id = dec2.entity_id inner join data_data dd on dd.id = dde.data_id inner join data_source ds on ds.id = dd.source_id where """ + get_where_clauses(request, where_clause) + """ group by dc.id order by count(dde.id) desc limit %s;""", [project_id, limit])
        rows = cursor.fetchall()
    
    for row in rows:
        response.append({
            'classificationID': row[0],
            'classificationLabel':row[1],
            'positiveCount': row[3],
            'negativeCount': row[4],
            'neutralCount': row[5],
        })
    
    return JsonResponse(response, safe=False)
