from .celery import app
from django.conf import settings
import requests
from data import models
from datetime import datetime
@app.task
def process_data(dict):
    try:
        resp = requests.post('{HOST}/v4/{APIKEY}/all.json'.format(
            HOST=settings.API_HOST, APIKEY=settings.APIKEY), data={'text': dict["text"], 'lang': dict["lang"]}).json()
        if 'score' in resp:
            sentiment = resp['score']
            source = models.Source.objects.get_or_create(label=dict["source"])[0]
            project = models.Project.objects.get(pk=dict["project_id"])
            data = models.Data(project=project, text=dict["text"], date_created=datetime.strptime(dict["date"], "%Y-%m-%d"), sentiment=sentiment, source=source, url=dict["url"], language=dict["lang"], weighted_score=0, relevance= 0, metadata=dict["metadata"])
            data.save()
    except Exception as e:
        print(e)