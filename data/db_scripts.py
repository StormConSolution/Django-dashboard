from django.db import models
from data.models import *
import requests


def add_data(project, source, text, lang, with_entities=False, aspect_model=None):
    sentiment = requests.post('http://api.repustate.com/v4/APIKEY/score.json',
                              {'text': text, 'lang': lang}).json()['score']

    entities = None
    if with_entities:
        entities = requests.post('http://api.repustate.com/v4/APIKEY/entities.json',
                                 {'text': text, 'lang': lang}).json()

    aspects = None
    if aspect_model is not None:
        aspects = requests.post('http://api.repustate.com/v4/APIKEY/aspect.json', {
                                'text': text, 'lang': lang, 'model': aspect_model}).json()

    data = Data.objects.create(
        project=project,
        source=source,
        text=text,
        language=lang
    )

    for ent in entities['entities']:
        Entity.objects.create(
            data=data,
            label=ent['title']
        )

    for key, value in aspects.items():
        if key != "status":
            for v in value:
                Aspect.objects.create(
                    data=data,
                    label=key,
                    chunk=v['chunk'],
                    sentiment=v['sentiment'],
                    topic=v['sentiment_topic'],
                    sentiment_text=v['sentiment_text']
                )
