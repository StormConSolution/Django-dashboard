import csv
import os
import psycopg2

from data.models import *

dsn = open(os.environ['PIPELINE_CONFIG']).read()
conn = psycopg2.connect(dsn)
cache = {}

def to_english(label, lang):
    # First make sure all of our english titles are in the interlanguage links table.
    if lang == 'en':
        return label

    key = '{}-{}'.format(label, lang)
    val = cache.get(key)
    if val:
        return val

    with conn.cursor() as cur:
        query = "SELECT englishpagetitle FROM interlanguagelinks_en WHERE pagetitle = %s and languagecode = %s"
        cur.execute(query, (label.replace(' ', '_'), lang))
        try:
            val = cur.fetchall()[0][0]
        except:
            return label

        cache[key] = val
        return val

def xrun():
    with open('entity_export.csv', 'w') as entity_out:
        w3 = csv.writer(entity_out)
        w3.writerow(['data_id', 'entity', 'english', 'classifications'])

        for d in Data.objects.filter(project__id=3155):
            for e in d.entities.prefetch_related('classifications'):
                w3.writerow([
                    d.id, 
                    e.label, 
                    to_english(e.label, d.language), 
                    ','.join(e.classifications.values_list('label', flat=True))
                ])


def run():
    with open('data_export.csv', 'w') as data_out:
        w = csv.writer(data_out)
        w.writerow(['id', 'date_created', 'text', 'url', 'language', 'location', 'source', 'raw sentiment', 'weighted_sentiment', 'relevance'])
        
        with open('aspect_export.csv', 'w') as aspect_out:
            w2 = csv.writer(aspect_out)
            w2.writerow(['data_id', 'label', 'sentiment', 'chunk', 'topic', 'sentiment text'])
            
            with open('entity_export.csv', 'w') as entity_out:
                w3 = csv.writer(entity_out)
                w3.writerow(['data_id', 'entity', 'english', 'classifications'])

                for d in Data.objects.filter(project__id=3155):
                    w.writerow([
                        d.id, 
                        d.date_created, 
                        d.text,
                        d.url,
                        d.language,
                        d.location, 
                        d.source.label, 
                        d.sentiment, 
                        d.weighted_score,
                        d.relevance])
                    
                    for a in d.aspect_set.all():
                        if a.sentiment_text:
                            st = a.sentiment_text[0]
                        else:
                            st = ''
                        w2.writerow([d.id, a.label, a.sentiment, a.chunk, a.topic, st])
                    
                    for e in d.entities.prefetch_related('classifications'):
                        w3.writerow([
                            d.id, 
                            e.label, 
                            to_english(e.label, d.language), 
                            ','.join(e.classifications.values_list('label', flat=True))
                        ])

