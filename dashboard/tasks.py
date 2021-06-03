import requests
from datetime import datetime

from django.conf import settings

from data import models
from .celery import app

@app.task
def process_data(arg):
    try:
        resp = requests.post('{HOST}/v4/{APIKEY}/all.json'.format(
            HOST=settings.API_HOST, APIKEY=settings.APIKEY), 
            data={'text': arg["text"], 'lang': arg["lang"]}).json()
        if 'score' in resp:
            sentiment = resp['score']
            if arg["source"] == '':
                source = models.Source.objects.get_or_create(label="Upload")[0]
            else:
                source = models.Source.objects.get_or_create(
                    label=arg["source"])[0]
            keywords = resp["keywords"]

            project = models.Project.objects.get(pk=arg["project_id"])

            if "date" not in arg.keys():
                date = datetime.now()
            else:
                date = datetime.strptime(arg["date"], "%Y-%m-%d") 
            data = models.Data(
                project=project, text=arg["text"], 
                date_created=date, 
                sentiment=sentiment, source=source, url=arg["url"], 
                language=arg["lang"], weighted_score=0, relevance= 0, 
                metadata=arg["metadata"],
                #keywords=keywords
            )

            for ent in resp['entities']:
                entity_instance, created = models.Entity.objects.get_or_create(
                    label=ent['title'],
                    language=arg["lang"],
                    english_label=ent['id'],
                )

                for clas in ent['classifications']:
                    c_instance, created = models.Classification.objects.get_or_create(
                        label=clas
                    )
                    entity_instance.classifications.add(c_instance)

                data.entities.add(entity_instance)

            if project.aspect_model:
                    aspects = requests.post(
                        '{HOST}/v4/{APIKEY}/aspect.json'.format(
                            HOST=settings.API_HOST, APIKEY=settings.APIKEY),
                            {
                                'text': arg["text"], 
                                'neutral': 1, 
                                'lang': arg["lang"], 
                                'model': project.aspect_model.label
                            }
                        ).json()
                    for key, value in aspects.items():
                        if key != "status" and aspects['status'] == 'OK':
                            for v in value:
                                models.Aspect.objects.create(
                                    data=data,
                                    label=key,
                                    chunk=v['chunk'],
                                    sentiment=v['score'],
                                    topic=v['sentiment_topic'],
                                    sentiment_text=v['sentiment_text']
                                )
            data.save()
    except Exception as e:
        print(e)