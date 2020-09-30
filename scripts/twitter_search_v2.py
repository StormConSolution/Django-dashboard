import argparse
import csv
import json
import os

import requests

# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'


def auth():
    return os.environ.get("TWITTER_BEARER_TOKEN")


def create_url(query, next_token=None):
    # Tweet fields are adjustable.
    # Options include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    tweet_fields = "tweet.fields=author_id,text,created_at,lang"
    url = "https://api.twitter.com/2/tweets/search/recent?query={}&max_results=100&{}".format(
        query, tweet_fields
    )
    if next_token:
        url += "&next_token=" + next_token
    return url


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint(url, headers):
    print("Searching", url)
    response = requests.request("GET", url, headers=headers)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def main(csvfile, query):
    bearer_token = auth()
    url = create_url(query)
    headers = create_headers(bearer_token)
    with open(csvfile, 'a') as fd:
        writer = csv.writer(fd)
        for i in range(10):
            json_response = connect_to_endpoint(url, headers)
            for tweet in json_response['data']:
                writer.writerow([
                    tweet['id'], 
                    tweet['author_id'],
                    tweet['text'],
                    tweet['created_at'],
                    tweet['lang']])
            
            next_token = json_response['meta'].get('next_token')
            if next_token:
                url = create_url(query, next_token)
            else:
                break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Search twitter')
    parser.add_argument('--csv', required=True)
    parser.add_argument('--search', required=True)
    parser.add_argument('--lang')
    args = parser.parse_args()
    
    query = args.search
    if args.lang:
        query = "\"{}\" lang:{}".format(query, args.lang)

    main(args.csv, query)
