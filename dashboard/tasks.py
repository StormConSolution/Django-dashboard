from datetime import datetime

from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.mail import send_mail
import requests

from .celery import app
from .sms import send_sms
from data import models
from data import weighted
from data.helpers import getAPIKEY

logger = get_task_logger(__name__)

@app.task
def process_data(kwargs):
    user = models.Project.objects.get(id=int(kwargs["project_id"])).users.all()[0]
    APIKEY = getAPIKEY(user)
    
    try:
        for key in ["url", "metadata"]:
            if key not in kwargs:
                kwargs[key] = ""
        logger.warn("Data received {} in process_data task".format(kwargs))

        resp = requests.post('{HOST}/v4/{APIKEY}/all.json'.format(
            HOST=settings.API_HOST, APIKEY=APIKEY), 
            data={'text': kwargs["text"], 'lang': kwargs["lang"]}).json()
        
        if 'score' in resp:
            sentiment = resp['score']
            if kwargs["source"] == '':
                source = models.Source.objects.get_or_create(label="Upload")[0]
            else:
                source = models.Source.objects.get_or_create(
                    label=kwargs["source"])[0]

            project = models.Project.objects.get(pk=kwargs["project_id"])

            date = kwargs.get('date', None)
            if not date:
                date = datetime.now()
            else:
                date = datetime.strptime(kwargs["date"], "%Y-%m-%d") 
            
            weight_kwargs = {'raw_score': sentiment}
            
            data = models.Data.objects.create(
                project=project,
                text=kwargs["text"], 
                date_created=date, 
                sentiment=sentiment,
                source=source,
                url=kwargs["url"], 
                language=kwargs["lang"],
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
                        HOST=settings.API_HOST, APIKEY=APIKEY),
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
                if alert and rule.should_notify():
                    notify(alert)

    except Exception as e:
        print(e)

def notify(alert):
    """
    Send out a notification about an alert that has been triggered.
    """
    if alert.rule.emails:
        r = send_mail(
            'Repustate Alert: {}'.format(alert.rule.name),
            '{}\n\n{}'.format(alert.title, alert.description),
            'no-reply@repustate.com',
            alert.rule.emails.split(','),
            fail_silently=False,
        )
        logger.warn("Response from send_mail for alert {}: {}".format(alert, r))

    if alert.rule.sms:
        body = 'Alert [{}] from {}: "{}" ...'.format(alert.rule.name, alert.data.source, alert.data.text[:100])
        for phone_number in alert.rule.sms.split(','):
            m = send_sms(body, phone_number)
            logger.warn("Response from sms for alert {}: {}".format(alert, m))
