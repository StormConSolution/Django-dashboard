import time

from django.conf import settings
import requests
from searchtweets import load_credentials, gen_rule_payload, collect_results

from django.core.mail import EmailMessage, mail_admins
from data.models import TwitterSearch, Project, ChartType

MAX_RESULTS = 3000

VALID_LANGS = [l[0] for l in settings.LANGUAGES]

def notify(ts):
    if not settings.DEBUG:
        message = 'Your request status is now {}'.format(ts.get_status_display())
        msg = EmailMessage(
            subject='Update about your Twitter Search {}'.format(ts.project_name),
            body=message,
            from_email='info@repustate.com',
            to=(ts.created_by.email,),
        )
        try:
            msg.send()
        except Exception as e:
            print(e)

def run():
    # This environment variable stores the path to a file with twitter
    # credentials.
    premium_search_args = load_credentials(os.environ.get("TWITTER_KEYS"),
            yaml_key="search_tweets_api", env_overwrite=False)
    
    while True:
        for ts in TwitterSearch.objects.filter(status=TwitterSearch.NOT_RUNNING):
            print("Running", ts)
            ts.status = TwitterSearch.RUNNING
            ts.save()
            notify(ts)
            
            rule = gen_rule_payload(ts.query, results_per_call=100)

            try:
                tweets = collect_results(rule, max_results=MAX_RESULTS, result_stream_args=premium_search_args)
                resp = requests.post('https://dashboard.repustate.com/create-project/', 
                        {'name':ts.project_name, 'username':ts.created_by.username})
                project_id = resp.json()['project_id']

                # Add the necessary chart types automatically.
                project = Project.objects.get(pk=project_id)
                for ct in ChartType.objects.all():
                    if ts.entities and ct.label in ('entity_table', 'emotional_entities'):
                        project.charts.add(ct)
                    elif ts.aspect_id and ct.label.startswith('aspect'):
                        project.charts.add(ct)
                    else:
                        project.charts.add(ct)
            except Exception as e:
                print(e)
                ts.status = TwitterSearch.ERROR
                ts.save()
                notify(ts)
                continue

            for tweet in tweets:
                post_data = dict(
                    source='Twitter',
                    text=tweet.text,
                    date=tweet.created_at_datetime.strftime('%Y-%m-%d'),
                )
                
                # Twitter does a bad job of detecting language.
                lang = tweet.lang
                if lang not in VALID_LANGS:
                    lang = 'en'
                
                if ts.entities:
                    post_data['with_entities'] = 1
                
                if ts.aspect_id:
                    post_data['aspect_model'] = ts.aspect.label

                try:
                    requests.post('https://dashboard.repustate.com/add-data/{}/'.format(project_id), data=post_data)
                except Exception as e:
                    print(e)
                    break

            ts.status = TwitterSearch.DONE
            ts.save()
            notify(ts)

        print("Sleeping ...")
        time.sleep(120)
