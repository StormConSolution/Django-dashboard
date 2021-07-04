import time
import requests
import os
import sys
from pathlib import Path
import json

sys.path.append(os.path.join(Path(__file__).parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dashboard.settings")
from django import setup
setup()


from django.conf import settings
from django.core.mail import EmailMessage
from searchtweets import load_credentials, gen_rule_payload, collect_results
from data.models import TwitterSearch, Project

from dashboard.tasks import process_data


MAX_RESULTS = 2

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
    # We rely on the environment variables to store our credentials.
    premium_search_args = load_credentials(None, yaml_key="search_tweets_api", env_overwrite=True)
    
    while True:
        for ts in TwitterSearch.objects.filter(status=TwitterSearch.NOT_RUNNING):
            print("Running", ts)
            ts.status = TwitterSearch.RUNNING
            ts.save()
            notify(ts)
            
            rule = gen_rule_payload(ts.query, results_per_call=100)

            try:
                tweets = collect_results(rule, max_results=MAX_RESULTS, result_stream_args=premium_search_args)
                post_data = {
                    'name':ts.project_name,
                    'username':ts.created_by.username,
                    'aspect_model':ts.aspect,
                }
                project, created = Project.objects.get_or_create(name=ts.project_name)
                if created:
                    project.users.add(ts.created_by)
                    project.save()

                if ts.aspect_id:
                    post_data['aspect_model'] = ts.aspect.label
            except Exception as e:
                print(e)
                ts.status = TwitterSearch.ERROR
                ts.save()
                notify(ts)
                continue

            for tweet in tweets:
                # Twitter does a bad job of detecting language.
                lang = tweet.lang
                #aux = json.dumps(tweet)
                if lang not in VALID_LANGS:
                    lang = 'en'
                post_data = dict(
                    source='Twitter',
                    text=tweet.text,
                    date=tweet.created_at_datetime.strftime('%Y-%m-%d'),
                    lang=lang,
                    url=tweet.most_unrolled_urls["expanded_url"]
                )
                
                if ts.entities:
                    post_data['with_entities'] = 1
                post_data["project_id"] = project.pk
                process_data.delay(post_data)

            ts.status = TwitterSearch.DONE
            ts.save()
            notify(ts)

        print("Sleeping ...")
        time.sleep(120)

if __name__ == "__main__":
    run()
