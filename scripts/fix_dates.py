import csv

from data.models import Data
from django.db import transaction

def run():
    with open('scripts/news_dates.csv') as fd:
        r = csv.reader(fd, delimiter='\t')
        with transaction.atomic():
            for row in r:
                if row:
                    url, date = row
                    if date == 'None':
                        continue
                    Data.objects.filter(url=url).update(date_created=date)
