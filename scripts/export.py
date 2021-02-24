import csv

from data.models import *

def run():
    with open('data_export.csv', 'w') as data_out:
        w = csv.writer(data_out)
        w.writerow(['id', 'text', 'url', 'language', 'source', 'raw sentiment', 'weighted_sentiment'])
        
        with open('aspect_export.csv', 'w') as aspect_out:
            w2 = csv.writer(aspect_out)
            w2.writerow(['data_id', 'label', 'sentiment', 'chunk', 'topic', 'sentiment text'])
            
            with open('entity_export.csv', 'w') as entity_out:
                w3 = csv.writer(entity_out)
                w3.writerow(['data_id', 'entity', 'classifications'])

                for d in Data.objects.filter(project__id=3155):
                    w.writerow([d.id, d.text, d.url, d.language, d.source.label, d.sentiment, d.weighted_score])
                    
                    for a in d.aspect_set.all():
                        if a.sentiment_text:
                            st = a.sentiment_text[0]
                        else:
                            st = ''
                        w2.writerow([d.id, a.label, a.sentiment, a.chunk, a.topic, st])
                    
                    for e in d.entities.all():
                        w3.writerow([d.id, e.label, ','.join(e.classifications.values_list('label', flat=True))])


