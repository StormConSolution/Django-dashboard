import csv

from data.models import Data
from django.db import transaction

def run():
    factor = 1.1149 / 6.0

    with transaction.atomic():
        for d in Data.objects.filter(text__icontains=0, relevance=0):
            count = d.text.lower().count('rolex')
            relevance = max(count * factor, 1.114945959)
            d.relevance = count
            d.save()

