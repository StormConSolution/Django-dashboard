import csv

from data.models import Data
from django.db import transaction

def run():
    with transaction.atomic():
        with open('scripts/news_results.csv') as fd:
            r = csv.reader(fd)
            for row in r:
                _, url = row
                ds = Data.objects.filter(url=url)
                if ds.count() > 1:
                    for d in ds[1:]:
                        d.delete()

