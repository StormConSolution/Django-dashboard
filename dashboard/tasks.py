from .celery import app
from django.conf import settings
import requests
from data import models
import datetime
@app.task
def process_data(dict):
    try:
        resp = requests.post('{HOST}/v4/{APIKEY}/all.json'.format(
            HOST=settings.API_HOST, APIKEY=settings.APIKEY), data={'text': dict["text"], 'lang': dict["lang"]}).json()
        if 'score' in resp:
            sentiment = resp['score']
            data = models.Data(project_id=dict["project_id"], text=dict["text"], date_created=datetime.datetime.now(), sentiment=sentiment, source_id=1, weighted_score=0, relevance= 0)
            print(data) 
            data.save()
        
    except Exception as e:
        print(e)
    print(resp)