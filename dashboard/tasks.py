import requests
from datetime import datetime

from django.conf import settings

from data import models
from data import weighted
from .celery import app
from .sms import send_sms

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
            
            weight_args['raw_score'] = sentiment
            weighted_score = weighted.calculate(**weight_args)
            
            data = models.Data.objects.create(
                project=project,
                text=arg["text"], 
                date_created=date, 
                sentiment=sentiment,
                source=source,
                url=arg["url"], 
                language=arg["lang"],
                weighted_score=weighted_score,
                relevance= 0, 
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
        
            aspects_found = set()
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
                            aspects_found.add(key)
                            models.Aspect.objects.create(
                                data=data,
                                label=key,
                                chunk=v['chunk'],
                                sentiment=v['score'],
                                topic=v['sentiment_topic'],
                                sentiment_text=v['sentiment_text']
                            )
            
            # Check if we have to send out any alerts based on the alert rules setup.
            for rule in project.alertrule_set.all():
                handled = False 
                if rule.keywords:
                    for kw in rule.keywords.split(','):
                        if kw in data.text:
                            handled = True
                            data_models.Alert.objects.create(
                                project=project,
                                data=data,
                                rule=rule,
                                title='Triggered because keyword {} detected'.format(kw),
                                description='Alert created for message: {}'.format(data.text)
                            )
                            break
                 
                if not handled and rule.aspect in aspects_found:
                    data_models.Alert.objects.create(
                        project=project,
                        data=data,
                        rule=rule,
                        title='Triggered because aspect {} detected'.format(rule.aspect),
                        description='Alert created for message: {}'.format(data.text)
                    )
                
                # Has this alert been triggered often enough? If so, notify.
                if rule.should_notify():
                    rule.notify()

    except Exception as e:
        print(e)