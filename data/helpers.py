from urllib import parse
import hmac
import json
from kombu.exceptions import EncodeError
import requests
import re

from django.conf import settings
from data.models import Project


def get_filters_sql(request):
    dateFrom = request.GET.get("date_from")
    dateTo = request.GET.get("date_to")
    if not dateFrom:
        dateFrom = ""
    if not dateTo:
        dateTo = ""
    filters = []
    if dateFrom != "":
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
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    languages = parse.unquote(request.GET.get("languages", "")).split(",")
    # sources = parse.unquote(request.GET.get("sources", "")).split(",")
    sources_id = request.GET.get("sourcesID", "").split(",")
    sentiment = request.GET.get("sentiment", "").lower()

    if sentiment == "positive":
        where_clauses.append("dd.sentiment > 0")
    elif sentiment == "neutral":
        where_clauses.append("dd.sentiment = 0")
    elif sentiment == "negative":
        where_clauses.append("dd.sentiment < 0")


    if not date_from:
        date_from = ""
    if not date_to:
        date_to = ""
    if re.match(r"(\D*\d){6,}", date_from):
        where_clauses.append("dd.date_created >= '" + date_from + "'")
    if re.match(r"(\D*\d){6,}", date_to):
        where_clauses.append("dd.date_created <= '" + date_to + "'")
    if languages != ['']:
        map(lambda x: "''%s''" % x, languages)
        where_clauses.append("dd.language in (%s)" % ("'" + "','".join(languages) + "'"))

    # if sources != ['']:
    if sources_id != ['']:
        # map(lambda x: "''%s''" % x, sources)
        # where_clauses.append('ds."label" in (%s)' % ("'" + "','".join(sources) + "'"))
        where_clauses.append('ds.id in (%s)' % (",".join(sources_id)))

    # GET parameters for metadata start all with prefix "filter_"
    for key, value in request.GET.items():
        if key.startswith("filter_"):
            key = parse.unquote(key[len("filter_"):])
            values = parse.unquote(value).split(",")
            if len(values) > 0:
                or_statements = []
                for value in values:
                    or_statements.append("dd.metadata @> '{}'".format(json.dumps({key: value})))
                where_clauses.append("(" + " or ".join(or_statements) + ")")
    return where_clauses


def get_order_by(request, default_order_by="", default_order_rule=""):
    if default_order_by == "":
        default_order_by = " dd.date_created"
    if default_order_rule == "":
        default_order_rule = "desc"

    order_by = request.GET.get("order-by", "")
    if order_by == "":
        order_by = default_order_by

    order_rule = request.GET.get("order-rule", "")
    if order_rule == "":
        order_rule = default_order_rule
    return " order by {} {} ".format(order_by, order_rule)


def get_where_clauses(request, where_clauses):
    filter_clauses = get_filters_sql2(request)
    where_clauses = where_clauses + filter_clauses
    return " and ".join(where_clauses)


def get_teammates(user):
    h = hmac.new(bytes(settings.HMAC_SECRET, 'utf8'), bytes(user.username, 'utf8'), 'sha256')
    hashkey = h.hexdigest()

    resp = requests.get("{}/credentials/teammates/{}/{}/".format(
        settings.AUTH_HOST,
        user.username,
        hashkey)).json()

    return resp


def get_api_keys(user):
    h = hmac.new(bytes(settings.HMAC_SECRET, 'utf8'), bytes(user.username, 'utf8'), 'sha256')
    hashkey = h.hexdigest()

    return requests.get("{}/credentials/fetch/{}/{}/".format(
        settings.AUTH_HOST,
        user.username,
        hashkey)).json()

def save_aspect_model(aspect_model):
    rules = list(aspect_model.aspectrule_set.all())

    body = {
        "name": aspect_model.label,
        "lang": aspect_model.language,
        "rules": []
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
           "/v4/{}/custom-aspect.json".format(aspect_model.api_key))

    req = requests.post(
        url=url,
        json=body
    )
    if req.status_code != 200:
        return False
    return True


def delete_aspect_model(aspect_model):
    url = (settings.API_HOST +
           "/v4/{}/custom-aspect.json".format(aspect_model.api_key))

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


def get_project_api_key(project_id):
    return Project.objects.get(id=project_id).api_key


def save_entity_model(entity_model):
    url = (settings.API_HOST +
           "/v4/{}/custom-entities.json".format(entity_model.api_key))
    aliases = entity_model.aliases.split(",")
    classifications = []

    for elem in entity_model.classifications.all():
        classifications.append(elem.label)

    body = {
        "title": entity_model.label,
        "lang": entity_model.language,
        "classifications": classifications
    }
    resp = requests.put(
        url=url,
        data=body
    )
    url = (settings.API_HOST +
           "/v4/{}/custom-aliases.json".format(entity_model.api_key))
    for alias in aliases:
        resp = requests.put(
            url=url,
            params={
                "title": entity_model.label,
                "lang": entity_model.language,
                "alias": alias,
            },
        )
    return True


def delete_entity_model(entity_model):
    url = (settings.API_HOST +
           "/v4/{}/custom-entities.json".format(entity_model.api_key))

    requests.delete(
        url=url,
        params={
            "title": entity_model.label
        }
    )
    return True
