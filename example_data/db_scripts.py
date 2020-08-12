

import django
import os
import json
import requests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')
django.setup()

# Model imports have to be after
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from data.models import *
from datetime import date
APIKEY = 'repustatedemopage'


def add_data(project, source, text, lang, with_entities=False, aspect_model=None, aspect=None, date=date.today()):

    sentiment = requests.post('http://api.repustate.com/v4/{APIKEY}/score.json'.format(
        APIKEY=APIKEY), {'text': text, 'lang': lang}).json()['score']

    entities = None
    if with_entities:
        entities = requests.post('http://api.repustate.com/v4/{APIKEY}/entities.json'.format(
            APIKEY=APIKEY), {'text': text, 'lang': lang}).json()

    aspects = None
    if aspect_model is not None:
        aspects = requests.post('http://api.repustate.com/v4/{APIKEY}/aspect.json'.format(
            APIKEY=APIKEY), {'text': text, 'lang': lang, 'model': aspect_model}).json()
    else:
        aspects = json.loads(aspect)

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

    for ent in entities['entities']:
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
    this_project = Project.objects.create(name=project_name)
    this_project.save()


def assign_user_to_project(project_id, user_id):
    this_project = get_object_or_404(Project, pk=project_id)
    this_project.users.add(User.objects.get(id=user_id))
    this_project.save


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
    # TODO add autoemail tor user created
    user = User.objects.create_user(username=name,
                                    email=email,
                                    password=password)
    return(user.id)
