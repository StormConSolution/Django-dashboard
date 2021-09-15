from datetime import datetime
import uuid
import logging

from celery.utils.log import get_task_logger
from dateutil import parser
from django.conf import settings
from django.contrib.postgres.search import SearchVector
from django.core.mail import send_mail
from django.db import connection
from django.db.models import Value, CharField
import fasttext
import requests

from .celery import app
from .sms import send_sms
from .nlp_phrases import nlp_phrase_lookup
from data import models as data_models
from data.helpers import get_project_api_key, get_api_keys


MAX_TWEETS = 3000
VALID_LANGS = [l[0] for l in settings.LANGUAGES]

# Load the model for fasttext.
lang_id_model = fasttext.load_model(settings.FASTTEXT_MODEL)
log = logging.getLogger()

@app.task
def process_data(kwargs):
    logs = {
        "correlation_id": str(uuid.uuid4())
    }
    # If data id is defined just run again the same data item
    existing_data_item = None
    if kwargs.get("data_id"):
        try:
            existing_data_item = data_models.Data.objects.get(pk=kwargs["data_id"])
        except:
            # Object does not exist.
            log.error('trying change data item that does not exist', extra={
                'data_id': kwargs["data_id"],
                **logs
            })
            return

        kwargs["lang"] = existing_data_item.language
        kwargs["text"] = existing_data_item.text
        kwargs["date"] = existing_data_item.date_created.strftime('%Y-%m-%d')
        kwargs["project_id"] = existing_data_item.project.id
        kwargs["metadata"] = existing_data_item.metadata
        
        kwargs["source"] = ""
        if existing_data_item.source:
            kwargs["source"] = existing_data_item.source.label
        
        kwargs["url"] = ""
        if existing_data_item.url:
            kwargs["url"] = existing_data_item.url 
    
    apikey = get_project_api_key(kwargs["project_id"])

    log.info("process celery task", extra={**kwargs, **logs})

    if not kwargs.get('lang'):
        # No language set; use language detection.

        try:
            prediction, _ = lang_id_model.predict(kwargs['text'])
            # The return value of `prediction` looks like: ('__label__en',)
            kwargs['lang'] = prediction[0].split('__label__')[1]
        except Exception as e:
            log.error("Error detecting language {}: {}".format(kwargs, e), extra={**logs, **kwargs})
            # Default to english.
            kwargs['lang'] = 'en'

    resp = requests.post('{HOST}/v4/{APIKEY}/all.json'.format(
        HOST=settings.API_HOST, APIKEY=apikey), 
        data={'text': kwargs["text"], 'lang': kwargs["lang"]}).json()

    if 'score' not in resp:
        log.error("Error processing {}: {}".format(kwargs, resp), extra={**logs, **kwargs})
        return

    sentiment = resp['score']
    keywords = resp['keywords']
    if kwargs["source"] == '':
        source = data_models.Source.objects.get_or_create(label="Upload")[0]
    else:
        source, _ = data_models.Source.objects.get_or_create(
            label=kwargs["source"])

    project = data_models.Project.objects.get(pk=kwargs["project_id"])

    if not kwargs.get('date'):
        date = datetime.now()
    else:
        date = parser.parse(kwargs['date'])
    
    data = data_models.Data.objects.create(
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
    
    # This will store addition text we want to search by.
    search_text = ''

    for ent in resp['entities']:
        entity_instance, created = data_models.Entity.objects.get_or_create(
            label=ent['title'],
            language=kwargs["lang"],
            english_label=ent['id'],
        )

        search_text = "{} {}".format(search_text, ent["title"])

        english_title = ent['id'].replace('_', ' ')
        if english_title != ent['title']:
            # Store the English too for non-english.
            search_text = "{} {}".format(search_text, english_title)

        for clas in ent['classifications']:
            c_instance, created = data_models.Classification.objects.get_or_create(
                label=clas
            )
            entity_instance.classifications.add(c_instance)
        
            # Add the natural language phrases for each entity/classification
            # here to our search index column.
            nlp_phrase = nlp_phrase_lookup.get(clas, '')
            search_text = "{} {} {}".format(search_text, ' '.join(clas.split('.')), nlp_phrase)

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
                    data_models.Aspect.objects.create(
                        data=data,
                        label=key,
                        chunk=v['chunk'],
                        sentiment=v['score'],
                        topic=v['sentiment_topic'],
                        sentiment_text=v['sentiment_text']
                    )
                    
                    search_text = "{} {}".format(search_text, key)
    
    data.search = SearchVector('text') + SearchVector(Value(search_text, output_field=CharField()))
    data.save()

    # Update our co-occurrence tables.
    with connection.cursor() as cursor:
        cursor.execute("select update_data_entity_aspect(%s)", [data.id])
        cursor.execute("select update_data_aspectspresent(%s)", [data.id])
    
    # Check if we have to send out any alerts based on the alert rules setup.
    for rule in project.alertrule_set.filter(active=True):
        alert = None
        if rule.keywords:
            for kw in rule.keywords.split(','):
                if kw in data.text:
                    alert = data_models.Alert.objects.create(
                        project=project,
                        data=data,
                        rule=rule,
                        title='Triggered because keyword {} detected'.format(kw),
                        description='Alert created for message: {}'.format(data.text)
                    )
                    break
         
        if not alert and rule.aspect in aspects_found:
            alert = data_models.Alert.objects.create(
                project=project,
                data=data,
                rule=rule,
                title='Triggered because aspect {} detected'.format(rule.aspect),
                description='Alert created for message: {}'.format(data.text)
            )
        
        # Has this alert been triggered often enough? If so, notify.
        if alert and rule.should_notify():
            notify(alert)

    if existing_data_item:
        # We delete the old one in the case we're updating an existing data item..
        existing_data_item.delete()

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
        log.warn("Response from send_mail for alert {}: {}".format(alert, r))

    if alert.rule.sms:
        body = 'Alert [{}] from {}: "{}" ...'.format(alert.rule.name, alert.data.source, alert.data.text[:100])
        for phone_number in alert.rule.sms.split(','):
            m = send_sms(body, phone_number)
            log.warn("Response from sms for alert {}: {}".format(alert, m))

@app.task
def job_complete(guid):
    ex = data_models.ExportComments.objects.get(guid=guid)
    
    ex.status = data_models.DONE
    ex.save()
    
    project = ex.project
    
    log.info("Data processing request complete for project {}".format(project.id))

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
    ts = data_models.TwitterSearch.objects.get(pk=job_id)
    ts.status = data_models.TwitterSearch.RUNNING
    ts.save()
    
    apikeys = get_api_keys(ts.created_by)
    if not apikeys.get("apikeys"):
        log.error("No API keys found for {}".format(ts.created_by))
        return
        
    project = data_models.Project.objects.create(
        name=ts.project_name,
        aspect_model=ts.aspect,
        api_key=apikeys['apikeys'][0]
    )
    project.users.add(ts.created_by)
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
    
    # TODO: Temporary hack until we get a better solution.
    twint.output.clean_lists()

    ts.status = data_models.TwitterSearch.DONE
    ts.save()

    job_complete.delay(project.pk)
