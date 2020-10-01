import time

import requests
from searchtweets import load_credentials, gen_rule_payload, collect_results

from data.models import TwitterSearch

MAX_RESULTS = 2000

def run():
    premium_search_args = load_credentials(".twitter_keys.yaml",
                                           yaml_key="search_tweets_api",
                                           env_overwrite=False)

    while True:
        for ts in TwitterSearch.objects.filter(status=TwitterSearch.NOT_RUNNING):
            print("Running", ts)
            ts.status = TwitterSearch.RUNNING
            ts.save()

            rule = gen_rule_payload(ts.query, results_per_call=100) # testing with a sandbox account

            tweets = collect_results(rule, max_results=MAX_RESULTS, result_stream_args=premium_search_args)
            
            try:
                resp = requests.post('https://dashboard.repustate.com/create-project/', 
                        {'name':ts.project_name, 'username':ts.created_by.username})
                project_id = resp.json()['project_id']
            except Exception as e:
                print(e)
                ts.status = TwitterSearch.ERROR
                ts.save()
                continue

            for tweet in tweets:
                post_data = dict(
                    source='Twitter',
                    text=tweet.text,
                    lang=tweet.lang,
                    date=tweet.created_at_datetime.strftime('%Y-%m-%d'),
                )
                
                if ts.entities:
                    post_data['with_entities'] = 1
                
                if ts.aspect:
                    post_data['aspect_model'] = ts.aspect.label

                try:
                    requests.post('https://dashboard.repustate.com/add-data/{}/'.format(project_id), data=post_data)
                except Exception as e:
                    print(e)
                    break

            ts.status = TwitterSearch.DONE
            ts.save()
        
        print("Sleeping ...")
        time.sleep(60)
