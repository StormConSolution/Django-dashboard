import time

import requests
from searchtweets import load_credentials, gen_rule_payload, collect_results

from data.models import TwitterSearch

def run():
    premium_search_args = load_credentials(".twitter_keys.yaml",
                                           yaml_key="search_tweets_api",
                                           env_overwrite=False)

    while True:
        for ts in TwitterSearch.objects.filter(completed=False):
            print("Running", ts)

            rule = gen_rule_payload(ts.query, results_per_call=100) # testing with a sandbox account

            tweets = collect_results(rule, max_results=5000, result_stream_args=premium_search_args)

            resp = requests.post('http://localhost:8000/create-project/', 
                    {'name':'Pizza Hut', 'username':ts.created_by.username})
            project_id = resp.json()['project_id']

            for tweet in tweets:
                post_data = dict(
                    source='Twitter',
                    text=tweet.text,
                    lang=tweet.lang,
                    date=tweet.created_at_datetime,
                )
                
                if ts.entities:
                    post_data['with_entities'] = 1
                
                if ts.aspect:
                    post_data['aspect_model'] = ts.aspect.label

                try:
                    requests.post('http://localhost:8000/add-data/{}/'.format(project_id), data=post_data)
                except Exception as e:
                    print(e)
                    break

            ts.completed = True
            ts.save()
        
        print("Sleeping ...")
        time.sleep(60)
