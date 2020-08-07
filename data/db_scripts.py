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
        aspects = requests.post('http://api.repustate.com/v4/APIKEY/aspect.json',
                                {'text': text, 'lang': lang, 'model': model}
                                ).json()

    data = Data.objects.create(
        project=project,
        source=source,
        text=text,
        language=lang
    )

    # TODO: iterate over entities and create new instances of Entity.
    # TODO: iterate over aspects and create new instances of Aspect.
