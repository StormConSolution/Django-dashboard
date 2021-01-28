import csv

from data.models import Data

def run():
    with open('youtube_dates.csv') as fd:
        r = csv.reader(fd)
        for i, row in enumerate(r):
            if i % 100 == 0:
                print(i)
            try:
                Data.objects.filter(url=row[0]).update(date_created=row[1].split('T')[0])
            except:
                print(row)

