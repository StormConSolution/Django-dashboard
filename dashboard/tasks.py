import requests
from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail

from data import models
from data import weighted
from .celery import app
from .sms import send_sms

@app.task
def process_data(kwargs):
    
    try:
        resp = requests.post('{HOST}/v4/{APIKEY}/all.json'.format(
            HOST=settings.API_HOST, APIKEY=settings.APIKEY), 
            data={'text': kwargs["text"], 'lang': kwargs["lang"]}).json()
        
        if 'score' in resp:
            sentiment = resp['score']
            if kwargs["source"] == '':
                source = models.Source.objects.get_or_create(label="Upload")[0]
            else:
                source = models.Source.objects.get_or_create(
                    label=kwargs["source"])[0]
            keywords = resp["keywords"]

            project = models.Project.objects.get(pk=kwargs["project_id"])

            date = kwargs.get('date', None)
            if not date:
                date = datetime.now()
            else:
                date = datetime.strptime(kwargs["date"], "%Y-%m-%d") 
            
            weight_kwargs = {'raw_score': sentiment}
            weighted_score = weighted.calculate(**weight_kwargs)
            
            data = models.Data.objects.create(
                project=project,
                text=kwargs["text"], 
                date_created=date, 
                sentiment=sentiment,
                source=source,
                url=kwargs["url"], 
                language=kwargs["lang"],
                weighted_score=weighted_score,
                relevance= 0, 
                metadata=kwargs["metadata"],
                #keywords=keywords
            )
            
            for ent in resp['entities']:
                entity_instance, created = models.Entity.objects.get_or_create(
                    label=ent['title'],
                    language=kwargs["lang"],
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
                            'text': kwargs["text"], 
                            'neutral': 1, 
                            'lang': kwargs["lang"], 
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
                alert = None
                if rule.keywords:
                    for kw in rule.keywords.split(','):
                        if kw in data.text:
                            alert = models.Alert.objects.create(
                                project=project,
                                data=data,
                                rule=rule,
                                title='Triggered because keyword {} detected'.format(kw),
                                description='Alert created for message: {}'.format(data.text)
                            )
                            break
                 
                if not alert and rule.aspect in aspects_found:
                    alert = models.Alert.objects.create(
                        project=project,
                        data=data,
                        rule=rule,
                        title='Triggered because aspect {} detected'.format(rule.aspect),
                        description='Alert created for message: {}'.format(data.text)
                    )
                
                # Has this alert been triggered often enough? If so, notify.
                if rule.should_notify():
                    alert_notify(rule, alert)

    except Exception as e:
        print(e)

@app.task
def alert_notify(rule, alert):
    """
    Send out a notification about an alert that hass been triggered.
    """
    if rule.emails:
        send_mail(
            'Repustate Alert: {}'.format(rule.name),
            '{}\n\n{}'.format(alert.title, alert.description),
            'no-reply@repustate.com',
            rule.emails.split(','),
            fail_silently=False,
        )

    if rule.sms:
        body = 'Alert [{}] from {}: "{}" ...'.format(rule.name, alert.data.source, alert.data.text[:100])
        for phone_number in rule.sms.split(','):
            send_sms(body, phone_number)
