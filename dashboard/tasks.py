from datetime import datetime
import requests

from celery.utils.log import get_task_logger
from dateutil import parser
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.postgres.search import SearchVector


from .celery import app
from .sms import send_sms
from data import models
from data.helpers import get_project_api_key

logger = get_task_logger(__name__)

MAX_TWEETS = 3000
VALID_LANGS = [l[0] for l in settings.LANGUAGES]

@app.task
def process_data(kwargs):
    #if data id is defined just run again the same data item
    print(kwargs)
    if kwargs["data_id"]:
        data_item = models.Data.objects.get(pk=kwargs["data_id"])
        kwargs["source"] = ""
        kwargs["url"] = ""
        if data_item:
            kwargs["lang"] = data_item.language
            kwargs["text"] = data_item.text
            if data_item.source:
                kwargs["source"] = data_item.source.label
            if data_item.url:
                kwargs["url"] = data_item.url 
            kwargs["date"] = str(data_item.date_created)
            kwargs["project_id"] = data_item.project.id
            kwargs["metadata"] = data_item.metadata
            data_item.delete()
        else:
            return
    print(kwargs)
    apikey = get_project_api_key(kwargs["project_id"])
    


    logger.info("Data received {} in process_data task".format(kwargs))

    search_text = kwargs["text"]
    if not kwargs.get('lang'):
        # No language set; use language detection.
        try:
            resp = requests.post('{HOST}/v4/{APIKEY}/detect-language.json'.format(
                HOST=settings.API_HOST, APIKEY=apikey), data={'text': kwargs["text"]})
            kwargs['lang'] = resp.json()['language']
        except Exception as e:
            logger.error("Error detecting language for {}: {}. HOST = {} APIKEY = {}. Response: {}".format(
                kwargs['text'], e, settings.API_HOST, apikey, resp.content))
            return

    resp = requests.post('{HOST}/v4/{APIKEY}/all.json'.format(
        HOST=settings.API_HOST, APIKEY=apikey), 
        data={'text': kwargs["text"], 'lang': kwargs["lang"]}).json()
    
    if 'score' not in resp:
        logger.error("Error processing {}: {}".format(kwargs, resp))
        return

    sentiment = resp['score']
    keywords = resp['keywords']
    if kwargs["source"] == '':
        source = models.Source.objects.get_or_create(label="Upload")[0]
    else:
        source = models.Source.objects.get_or_create(
            label=kwargs["source"])[0]

    project = models.Project.objects.get(pk=kwargs["project_id"])

    if not kwargs.get('date'):
        date = datetime.now()
    else:
        date = parser.parse(kwargs['date'])
    
    data = models.Data.objects.create(
        project=project,
        text=kwargs["text"], 
        date_created=date, 
        sentiment=sentiment,
        source=source,
        url=kwargs.get("url", ''), 
        language=kwargs["lang"],
        relevance= 0, 
        metadata=kwargs.get("metadata", ''),
        keywords=keywords,
    )
    
    for ent in resp['entities']:
        entity_instance, created = models.Entity.objects.get_or_create(
            label=ent['title'],
            language=kwargs["lang"],
            english_label=ent['id'],
        )

        search_text = "{} {}".format(search_text, ent["title"])

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
                HOST=settings.API_HOST, APIKEY=apikey),
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
                    search_text = "{} {}".format(search_text, key)
                    models.Aspect.objects.create(
                        data=data,
                        label=key,
                        chunk=v['chunk'],
                        sentiment=v['score'],
                        topic=v['sentiment_topic'],
                        sentiment_text=v['sentiment_text']
                    )
    
    data.search = search_text
    data.save()
    
    # Check if we have to send out any alerts based on the alert rules setup.
    for rule in project.alertrule_set.filter(active=True):
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

@app.task
def job_complete(project_id):
    project = models.Project.objects.get(pk=project_id)
    
    logger.info("Data processing request complete for project {}".format(project_id))

    # Send an email to all people on this project.
    if not settings.DEBUG:
        msg = 'We have completed processing your latest data processing request for project "{}"'.format(project.name)
        
        send_mail(
            'Repustate Data Processing Complete',
            msg,
            'no-reply@repustate.com',
            [u.email for u in project.users.all()],
            fail_silently=False
        )

@app.task
def process_twitter_search(job_id):
    ts = models.TwitterSearch.objects.get(pk=job_id)
    ts.status = models.TwitterSearch.RUNNING
    ts.save()
        
    project, _ = models.Project.objects.get_or_create(name=ts.project_name)
    project.users.add(ts.created_by)
    project.aspect_model = ts.aspect
    # NOTE: change this to the user's API key when we introduce this feature to
    # all users.
    project.api_key = settings.APIKEY
    project.save()

    import twint
    config = twint.Config()
    config.Limit = MAX_TWEETS
    config.Store_object = True
    config.Search = ts.query
    twint.run.Search(config)

    for tweet in twint.output.tweets_list:
        # NOTE: Twitter often does a bad job of detecting language.
        lang = tweet.lang
        if lang not in VALID_LANGS:
            lang = 'en'
        
        post_data = dict(
            source='Twitter',
            text=tweet.tweet,
            date=tweet.datestamp,
            lang=lang,
            url=tweet.link,
            project_id=project.pk,
        )
        
        process_data.delay(post_data)

    ts.status = models.TwitterSearch.DONE
    ts.save()

    job_complete.delay(project.pk)
