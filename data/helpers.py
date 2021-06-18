from urllib import parse
import hmac
import requests

from django.conf import settings
from django.contrib.auth.models import User
from requests.api import request
from data import models

def get_filters_sql(request):
    dateFrom = request.GET.get("date-from")
    dateTo = request.GET.get("date-to")
    if not dateFrom:
        dateFrom = ""
    if not dateTo:
        dateTo = ""
    filters = []
    if dateFrom != "" :
        filters.append("dd.date_created >= '" + dateFrom + "'")
    if dateTo != "":
        filters.append("dd.date_created <= '" + dateTo + "'")
    filtersSQL = " and ".join(filters)
    if filtersSQL != "":
        filtersSQL = " and " + filtersSQL
    else:
        filtersSQL = ""
    return filtersSQL

def get_filters_sql2(request):
    where_clauses = []
    dateFrom = request.GET.get("date-from")
    dateTo = request.GET.get("date-to")
    languages =parse.unquote(request.GET.get("languages", "")).split(",")
    #sources = parse.unquote(request.GET.get("sources", "")).split(",")
    sourcesID = request.GET.get("sourcesID", "").split(",")
    if not dateFrom:
        dateFrom = ""
    if not dateTo:
        dateTo = ""
    if dateFrom != "" :
        where_clauses.append("dd.date_created >= '" + dateFrom + "'")
    if dateTo != "":
        where_clauses.append("dd.date_created <= '" + dateTo + "'")
    if languages != ['']:
        map(lambda x: "''%s''" % x, languages)
        where_clauses.append("dd.language in (%s)" % ("'" + "','".join(languages) + "'"))

    #if sources != ['']:
    if sourcesID != ['']:
        #map(lambda x: "''%s''" % x, sources)
        #where_clauses.append('ds."label" in (%s)' % ("'" + "','".join(sources) + "'"))
        where_clauses.append('ds.id in (%s)' % (",".join(sourcesID)))
    return where_clauses

def get_where_clauses(request, where_clauses):
    filter_clauses = get_filters_sql2(request)
    where_clauses = where_clauses + filter_clauses
    return " and ".join(where_clauses)

def get_api_key(user: User) -> str:
    h = hmac.new(bytes(settings.HMAC_SECRET, 'utf8'), bytes(user.email, 'utf8'), 'sha256')
    hashkey = h.hexdigest()
    resp = requests.get("{}/credentials/fetch/{}/{}/".format(
        settings.AUTH_HOST,
        user.email,
        hashkey)).json()
    
    if len(resp['apikeys']) > 0:
        return resp['apikeys'][0]
    return ""

def save_aspect_model(apikey: str, aspect_model: models.AspectModel) -> bool:
    rules: list[models.AspectRule] = list(aspect_model.aspectrule_set.all())

    body = {
        "name": aspect_model.label,
        "lang": aspect_model.language,
        "rules":[]
    }

    for rule in rules:
        request_rule = {
            "name": rule.rule_name,
            "terms": rule.definition,
            "classifications": rule.classifications,
        }
        if rule.predefined:
            request_rule["predefinedAspect"] = rule.rule_name
        body["rules"].append(request_rule)

    url = (settings.API_HOST + 
    "/v4/{}/custom-aspect.json".format(apikey))

    req = requests.post(
        url=url,
        json=body
    )

    if req.status_code != 200:
        return False
    return True

def delete_aspect_model(apikey: str, aspect_model: models.AspectModel) -> bool:
    url = (settings.API_HOST + 
    "/v4/{}/custom-aspect.json".format(apikey))

    body = {
        "name": aspect_model.label,
        "lang": aspect_model.language,
    }

    req = requests.delete(
        url=url,
        json=body
    )
    if req.status_code != 200 and req.status_code != 404:
        return False
    return True
