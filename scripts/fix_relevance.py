import csv

from data.models import Data
from django.db import transaction

def run():
    factor = 1.1149 / 6.0

    with transaction.atomic():
        for d in Data.objects.filter(text__icontains='rolex', project=3155):
            count = d.text.lower().count('rolex')
            relevance = min(count * factor, 1.114945959)
            d.relevance = relevance
            d.save()

