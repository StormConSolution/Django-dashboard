from datetime import date
import json
import os

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')
django.setup()

# Model imports have to be after
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from data.models import *
import requests

APIKEY = 'repustatedemopage'
HOST = 'http://localhost:9000'

def add_data(project, source, text, lang, with_entities=False, aspect_model=None, default_aspect=None, date=date.today()):

    sentiment = requests.post('{HOST}/v4/{APIKEY}/score.json'.format(
        HOST=HOST, APIKEY=APIKEY), {'text': text, 'lang': lang}).json()['score']

    source, _ = Source.objects.get_or_create(label=source)

    data = Data.objects.create(
        date_created=date,
        project=project,
        source=source,
        text=text,
        sentiment=sentiment,
        language=lang,
    )
    emotions = []
    found_entities = []

    entities = {}
    if with_entities:
        entities = requests.post('{HOST}/v4/{APIKEY}/entities.json'.format(
            HOST=HOST, APIKEY=APIKEY), {'text': text, 'lang': lang}).json()

    for ent in entities.get('entities', []):
        entity_instance, created = Entity.objects.get_or_create(
            label=ent['title']
        )

        is_emotion = False

        for clas in ent['classifications']:
            c_instance, created = Classification.objects.get_or_create(
                label=clas
            )
            entity_instance.classifications.add(c_instance)

            if clas == 'Person.emotion':
                is_emotion = True
                emotion_instance, created = Emotion.objects.get_or_create(
                    label=ent['title']
                )
                emotions.append(emotion_instance)

        if not is_emotion:
            found_entities.append(entity_instance)

        data.entities.add(entity_instance)

    for entity in found_entities:
        for emotion in emotions:
            EmotionalEntity.objects.create(
                emotion=emotion, entity=entity, data=data)
    
    aspects = {}
    if aspect_model is not None:
        aspects = requests.post('{HOST}/v4/{APIKEY}/aspect.json'.format(
            HOST=HOST, APIKEY=APIKEY), {'text': text, 'lang': lang, 'model': aspect_model}).json()
    elif default_aspect:
        aspects = json.loads(default_aspect)

    for key, value in aspects.items():
        if key != "status":
            for v in value:
                Aspect.objects.create(
                    data=data,
                    label=key,
                    chunk=v['chunk'],
                    sentiment=v['score'],
                    topic=v['sentiment_topic'],
                    sentiment_text=v['sentiment_text']
                )


def create_new_project(project_name):
    return Project.objects.create(name=project_name)

def assign_user_to_project(project, user):
    project.users.add(user)

def add_chart_to_project(project_id, chart_type, chart_size):
    this_project = get_object_or_404(Project, pk=project_id)
    c, create = Chart.objects.get_or_create(
        chart_type=chart_type,
        chart_size=chart_size
    )
    c.project.add(this_project)

def remove_chart_from_project():
    pass

def create_user(name, email, password):
    # TODO add autoemail to user created
    return User.objects.create_user(
            username=name,
            email=email,
            password=password
        )
