"""
Interactions with the Repustate API server.
"""
import json

from django.conf import settings
import requests

def api_request(method, url, data=None, params=None, json=None):
    """
    Send API call to Repustate server. Check response and return True/False plus JSON response.
    """
    raw_resp = method(url, data=data, params=params, json=json)
    try:
        resp = raw_resp.json()
    except json.JSONDecodeError:
        return False, {'status':'Fail', 'description':'Repustate API server error'}

    return resp['status'] == 'OK', resp

def add_sentiment_rule(api_key, data):
    url = '{}/v4/{}/sentiment-rules.json'.format(settings.API_HOST, api_key)
    return api_request(requests.post, url, data=data)

def delete_sentiment_rule(sentiment_rule):
    url = "{}/v4/{}/sentiment-rules.json?rule_id=%s".format(
            settings.API_HOST, sentiment_rule.api_key, sentiment_rule.rule_id)
    return api_request(requests.delete, url)

def save_aspect_model(aspect_model):
    body = {
        "name": aspect_model.label,
        "lang": aspect_model.language,
        "rules": []
    }

    rules = aspect_model.aspectrule_set.all()

    for rule in rules:
        request_rule = {
            "name": rule.rule_name,
            "terms": rule.definition,
            "classifications": rule.classifications,
        }
        if rule.predefined:
            request_rule["predefinedAspect"] = rule.rule_name
        body["rules"].append(request_rule)

    url = settings.API_HOST + "/v4/{}/custom-aspect.json".format(aspect_model.api_key)
    
    return api_request(requests.post, url, json=body)


def delete_aspect_model(aspect_model):
    url = settings.API_HOST + "/v4/{}/custom-aspect.json".format(aspect_model.api_key)

    body = {
        "name": aspect_model.label,
        "lang": aspect_model.language,
    }
    
    return api_request(requests.delete, url, json=body)

def add_entity_model(entity_model):
    url = settings.API_HOST + "/v4/{}/custom-entities.json".format(entity_model.api_key)
    classifications = []

    for elem in entity_model.classifications.all():
        classifications.append(elem.label)

    body = {
        "title": entity_model.label,
        "lang": entity_model.language,
        "classifications": classifications
    }

    result, resp = api_request(requests.put, url, data=body)
    if not result:
        return False, resp

    url = settings.API_HOST + "/v4/{}/custom-aliases.json".format(entity_model.api_key)
    
    if entity_model.aliases:
        aliases = entity_model.aliases.split(",")
        for alias in aliases:
            params={
                "title": entity_model.label,
                "lang": entity_model.language,
                "alias": alias,
            }
            result, resp = api_request(requests.put, url, params=params)
            if not result:
                return False, resp
    
    return True, {'status':'OK'}

def delete_entity_model(entity_model):
    url = settings.API_HOST + "/v4/{}/custom-entities.json".format(entity_model.api_key)

    params={
        "title": entity_model.label
    }
    
    return api_request(requests.delete, url, params=params)
