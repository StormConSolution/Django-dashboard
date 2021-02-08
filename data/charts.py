from functools import reduce
from operator import or_
from operator import itemgetter
import datetime
import json

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db import connection
from django.db.models import Count, Q, F

from data import models as data_models
from data.models import Entity, Data, Aspect, Source, Country

DEFAULT_COLORS = [
    "rgba(13, 19, 33, 1)",
    "rgba(29, 45, 68, 1)",
    "rgba(62, 92, 118, 1)",
    "rgba(116, 140, 171, 1)",
    "rgba(240, 235, 216, 1)",
    "rgba(131, 181, 209, 1)",
    "rgba(105, 153, 93, 1)",
    "rgba(203, 172, 136, 1)",
    "rgba(237, 182, 163, 1)",
]

COLORS = {
    'positive': 'rgb(83,127,214)',
    'negative': 'rgb(221,153,66)',
    'neutral': 'rgba(67, 99, 216,0.5)',
    'contrasts': DEFAULT_COLORS
}


class BaseChart:

    def __init__(self, project, start, end, entity_filter, aspect_topic, aspect_name, lang_filter, source_filter):
        self.project = project
        
        if not end:
            end = project.most_recent_date()
        self.end = end
    
        if not start:
            start = self.end - datetime.timedelta(days=30)
        self.start = start

        self.entity_filter = entity_filter
        self.aspect_topic = aspect_topic
        self.aspect_name = aspect_name
        self.lang_filter = lang_filter
        self.source_filter = source_filter

    def render_data(self):
        """
        Returns the data necessary to render a chart in JavaScript.
        """
        raise NotImplementedError
    

class EntityTable(BaseChart):

    def render_data(self):
        
        entity_data_set = Data.objects.filter(
            project=self.project, date_created__range=(self.start, self.end))

        if self.entity_filter:
            entity_data_set = entity_data_set.filter(
                entities__label=self.entity_filter)

        if self.aspect_topic:
            entity_data_set = entity_data_set.filter(
                aspect__topic=self.aspect_topic)
        
        if self.aspect_name:
            entity_data_set = entity_data_set.filter(
                aspect__label=self.aspect_name)
        
        if self.lang_filter and self.lang_filter[0]:
            entity_data_set = entity_data_set.filter(
                language__in=self.lang_filter)
        
        if self.source_filter and self.source_filter[0]:
            entity_data_set = entity_data_set.filter(
                reduce(or_, [Q(source__label=c)for c in self.source_filter]))
        
        entity_set = Entity.objects.filter(data__in=entity_data_set)
        entity_count = entity_set.annotate(
            data_count=models.Count('data')).prefetch_related('classifications').order_by('-data_count')[:500]
        entities = {"data": []}

        for ec in entity_count:
            entities["data"].append([
                ec.label,
                ', '.join([str(c) for c in ec.classifications.all()]),
                ec.data_count
            ])

        return entities


class CountriesTable(BaseChart):

    def render_data(self):
        # Show sentiment by county.
        result = {}

        result['country_labels'] = []

        positive = {'label': 'positive', 'data': [],
                    'backgroundColor': COLORS['positive']}
        negative = {'label': 'negative', 'data': [],
                    'backgroundColor': COLORS['negative']}
        
        data_set = Data.objects.filter(
            project=self.project, date_created__range=(self.start, self.end))

        if self.entity_filter:
            data_set = data_set.filter(
                entities__label=self.entity_filter)

        if self.aspect_topic:
            data_set = data_set.filter(
                aspect__topic=self.aspect_topic)
        
        if self.aspect_name:
            data_set = data_set.filter(
                aspect__label=self.aspect_name)
        
        if self.lang_filter and self.lang_filter[0]:
            data_set = data_set.filter(
                language__in=self.lang_filter)
        
        for country in Country.objects.values_list('label', flat=True):
            pos_total = data_set.filter(country__label=country, sentiment__gt=0).count()
            neg_total = data_set.filter(country__label=country, sentiment__lt=0).count()

            if pos_total or neg_total:
                result['country_labels'].append(country)
                positive['data'].append(pos_total)
                negative['data'].append(neg_total)

        result['country_datasets'] = [positive, negative]

        return result


class DataEntryTable(BaseChart):

    def render_data(self):
        
        entry_data_set = Data.objects.filter(
            project=self.project, date_created__range=(self.start, self.end))

        if self.entity_filter:
            entry_data_set = entry_data_set.filter(
                entities__label=self.entity_filter)

        if self.aspect_topic:
            entry_data_set = entry_data_set.filter(
                aspect__topic=self.aspect_topic)
        
        if self.aspect_name:
            entry_data_set = entry_data_set.filter(
                aspect__label=self.aspect_name)
        
        if self.lang_filter and self.lang_filter[0]:
            entry_data_set = entry_data_set.filter(
                language__in=self.lang_filter)
        
        if self.source_filter and self.source_filter[0]:
            entry_data_set = entry_data_set.filter(
                reduce(or_, [Q(source__label=c)for c in self.source_filter]))

        entry_data = {"data": []}
        
        for entry in entry_data_set.values('date_created', 'text', 
                'source__label', 'weighted_score', 'url', 'sentiment', 'country__label')[:1000]:
            
            # We encode the URL and text in json string and decode it client side.
            text = {"text": entry["text"][:300], "url": entry["url"]}

            entry_data["data"].append([
                entry['date_created'],
                json.dumps(text),
                entry['source__label'],
                round(entry['weighted_score'], 4),
                round(entry['sentiment'], 4), 
                entry['country__label'],
            ])

        return entry_data


class AspectTopicTable(BaseChart):

    def render_data(self):
        aspect_set = Aspect.objects.filter(
            data__date_created__range=(self.start, self.end),
            data__project=self.project
        )
        
        if self.entity_filter:
            aspect_set = aspect_set.filter(
                data__in=Data.objects.filter(entities__label=self.entity_filter))
        if self.aspect_topic:
            aspect_set = aspect_set.filter(
                data__in=Data.objects.filter(aspect__topic=self.aspect_topic))
        if self.aspect_name:
            aspect_set = aspect_set.filter(
                data__in=Data.objects.filter(aspect__label=self.aspect_name))
        if self.lang_filter and self.lang_filter[0]:
            aspect_set = aspect_set.filter(
                data__in=Data.objects.filter(reduce(or_, [Q(language=c)for c in self.lang_filter])))
        if self.source_filter and self.source_filter[0]:
            aspect_set = aspect_set.filter(
                data__in=Data.objects.filter(reduce(or_, [Q(source__label=c)for c in self.source_filter])))

        aspect_count = aspect_set.values_list('topic', 'label').annotate(
            topic_count=Count('topic')).order_by('-topic_count')
        
        aspects = {"data": []}
        for topic, label, count in aspect_count:
            aspects["data"].append([
                topic,
                label,
                count
            ])

        return aspects

class AspectNameTable(BaseChart):

    def render_data(self):
        aspect_set = Aspect.objects.filter(
            data__date_created__range=(self.start, self.end),
            data__project=self.project
        )
        if self.entity_filter:
            aspect_set = aspect_set.filter(
                data__in=Data.objects.filter(entities__label=self.entity_filter))
        if self.aspect_topic:
            aspect_set = aspect_set.filter(
                data__in=Data.objects.filter(aspect__topic=self.aspect_topic))
        if self.aspect_name:
            aspect_set = aspect_set.filter(
                data__in=Data.objects.filter(aspect__label=self.aspect_name))
        if self.lang_filter and self.lang_filter[0]:
            aspect_set = aspect_set.filter(
                data__in=Data.objects.filter(reduce(or_, [Q(language=c)for c in self.lang_filter])))
        if self.source_filter and self.source_filter[0]:
            aspect_set = aspect_set.filter(
                data__in=Data.objects.filter(reduce(or_, [Q(source__label=c)for c in self.source_filter])))

        aspect_count = aspect_set.values_list('label').annotate(
            label_count=Count('label')).order_by('-label_count')

        aspects = {"data": []}
        for label, count in aspect_count:
            aspects["data"].append([
                label,
                Aspect.objects.filter(label=label)[0].label,
                count
            ])

        return aspects


class SentimenFrequencyTable(BaseChart):

    def render_data(self):
        data_set = Data.objects.filter(
            project=self.project,
            date_created__range=(self.start, self.end)
        )

        if self.entity_filter:
            data_set = data_set.filter(entities__label=self.entity_filter)
        if self.aspect_topic:
            data_set = data_set.filter(aspect__topic=self.aspect_topic)
        if self.aspect_name:
            data_set = data_set.filter(aspect__label=self.aspect_name)
        if self.lang_filter and self.lang_filter[0]:
            data_set = data_set.filter(
                reduce(or_, [Q(language=c)for c in self.lang_filter]))
        if self.source_filter and self.source_filter[0]:
            data_set = data_set.filter(
                reduce(or_, [Q(source__label=c)for c in self.source_filter]))

        sentiment_f = data_set.aggregate(
            positive=Count('sentiment', filter=Q(sentiment__gt=0)),
            negative=Count('sentiment', filter=Q(sentiment__lt=0)),
            neutral=Count('sentiment', filter=Q(sentiment=0))
        )

        sentiment_f_data = list(sentiment_f.values())
        
        resp = {"sentiment_f_data": sentiment_f_data}
        resp['total_data'] = sum(sentiment_f_data)
        resp['total_positive'] = sentiment_f_data[0]
        resp['total_negative'] = sentiment_f_data[1]

        return resp

class SentimentTimeTable(BaseChart):

    def render_data(self):
        data_set = Data.objects.filter(
            project=self.project,
            date_created__range=(self.start, self.end)
        )

        if self.entity_filter:
            data_set = data_set.filter(entities__label=self.entity_filter)
        if self.aspect_topic:
            data_set = data_set.filter(aspect__topic=self.aspect_topic)
        if self.aspect_name:
            data_set = data_set.filter(aspect__label=self.aspect_name)
        if self.lang_filter and self.lang_filter[0]:
            data_set = data_set.filter(
                reduce(or_, [Q(language=c)for c in self.lang_filter]))
        if self.source_filter and self.source_filter[0]:
            data_set = data_set.filter(
                reduce(or_, [Q(source__label=c)for c in self.source_filter]))

        sentiment_t = data_set.values('date_created').annotate(
            positive=Count('sentiment', filter=Q(sentiment__gt=0)),
            negative=Count('sentiment', filter=Q(sentiment__lt=0)),
        ).order_by('date_created')

        result = {'sentiment_t_labels': []}
        for sentiment in list(sentiment_t):
            result['sentiment_t_labels'].append(sentiment['date_created'])

        positive = {'name': 'Positive', 'label': 'Positive', 'data': list(map(lambda d: d['positive'], list(sentiment_t))),
                    'backgroundColor': COLORS['positive'], 'borderColor': COLORS['positive'], "fill": False, }
        negative = {'name': 'Negative', 'label': 'Negative', 'data': list(map(lambda d: d['negative'], list(sentiment_t))),
                    'backgroundColor': COLORS['negative'], 'borderColor': COLORS['negative'], "fill": False}
        result['sentiment_t_data'] = [positive, negative]

        return result

class DataBySourceTable(BaseChart):
    """
    Compute our volume by source stats.
    """
    
    def render_data(self):
        
        source_by_count = {
            'series':[],
            'labels':[],
        }
        
        total = 0
        
        SOURCE_QUERY = """
        SELECT 
            REPLACE(data_source.label, 'www.', ''),
            COUNT(data_data.source_id)
        FROM 
            %s
        WHERE 
            %s
        GROUP BY data_source.label
        ORDER BY COUNT(data_data.source_id) DESC
        LIMIT 15
        """

        tables = [
            'data_data',
            'data_source',
        ]

        where_clause = [
            'data_source.id = data_data.source_id',
            'data_data.project_id = %s',
            'data_data.date_created between %s AND %s',
        ]
        query_args = [self.project.id, self.start, self.end]

        if self.lang_filter:
            lang_string = len(self.lang_filter) * '%s,'
            where_clause.append('data_data.language IN ({})'.format(lang_string[:-1]))
            query_args.extend(self.lang_filter)
        
        if self.source_filter:
            source_string = len(self.source_filter) * '%s,'
            where_clause.append('data_data.source_id IN ({})'.format(source_string[:-1]))
            # Get the raw IDs for our sources.
            source_ids = data_models.Source.objects.filter(
                    label__in=self.source_filter).values_list('id', flat=True)
            query_args.extend(source_ids)
        
        if self.aspect_topic or self.aspect_name:
            tables.append('data_aspect')
            where_clause.append('data_data.id=data_aspect.data_id')

            if self.aspect_topic:
                where_clause.append('data_aspect.topic = %s')
                query_args.append(self.aspect_topic)
        
            if self.aspect_name:
                where_clause.append('data_aspect.label = %s')
                query_args.append(self.aspect_name)

        total = 0
        with connection.cursor() as cursor:
            cursor.execute(SOURCE_QUERY % (','.join(tables), ' AND '.join(where_clause)), query_args)
            for idx, row in enumerate(cursor.fetchall()):
                total += row[1]
                source_by_count['labels'].append(row[0])
                source_by_count['series'].append(row[1])
        
        source_by_count['total'] = total
        
        return {'source_by_count': source_by_count}

CHART_LOOKUP = {
    'aspect_table': AspectTopicTable,
    'entity_table': EntityTable,
    'data_entrytable': DataEntryTable,
    'sentiment_f': SentimenFrequencyTable,
    'sentiment_t': SentimentTimeTable,
    'countries_t': CountriesTable,
    'data_source_table': DataBySourceTable,
}
