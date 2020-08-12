
import django
import os
import json
import requests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')
django.setup()

from datetime import date
# Model imports have to be after
from data.models import *
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

APIKEY = 'repustatedemopage'


def add_data(project, source, text, lang, with_entities=False, aspect_model=None, aspect=None,date = date.today()):

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

    data = Data.objects.create(
        date_created=date,
        project=project,
        source=source,
        text=text,
        sentiment=sentiment,
        language=lang,
        keywords=()
    )

    for ent in entities['entities']:
        entity_instance, created = Entity.objects.get_or_create(
            label=ent['title']
        )

        for clas in ent['classifications']:
            c_instance, created = Classification.objects.get_or_create(
                label=clas
            )
            entity_instance.classifications.add(c_instance)

        data.entities.add(entity_instance)

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


def add_chart_to_project(project_id,chart_type,chart_size):
    this_project = get_object_or_404(Project, pk=project_id)
    c,create = Chart.objects.get_or_create(
        chart_type=chart_type,
        chart_size = chart_size
    )
    c.project.add(this_project)
    


def remove_chart_from_project():
    pass


def create_user():
    #TODO improve logic for user creation
    user = User.objects.create_user(username='john',
                                    email='jlennon@beatles.com',
                                    password='glass onion')
    return(user.id)
