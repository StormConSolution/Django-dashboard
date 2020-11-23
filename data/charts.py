import datetime
from django.db import models
from data import models as data_models
from django.db.models import Count, Q, F
from operator import or_
from functools import reduce
from django.core.exceptions import ObjectDoesNotExist


from data.models import Entity, Data, Aspect, Source, EmotionalEntity, Keyword, Country

from operator import itemgetter

DEFAULT_COLORS = ['rgba(230, 25, 75,0.5)',
                  'rgba(60, 180, 75,0.5)',
                  'rgba(255, 225, 25,0.5)',
                  'rgba(67, 99, 216,0.5)',
                  'rgba(245, 130, 49,0.5)',
                  'rgba(66, 212, 244,0.5)',
                  'rgba(240, 50, 230,0.5)',
                  'rgba(250, 190, 212,0.5)',
                  'rgba(70, 153, 144,0.5)',
                  'rgba(220, 190, 255,0.5)',
                  'rgba(255, 250, 200,0.5)',
                  'rgba(128, 0, 0,0.5)',
                  'rgba(170, 255, 195,0.5)',
                  'rgba(0, 0, 117,0.5)'
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
        self.start = start
        self.end = end
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


class TopEntityTable(BaseChart):

    def render_data(self):
        # prior 7 days
        today = datetime.datetime.today()
        datetime_start = today - datetime.timedelta(days=7)
        entity_set = Entity.objects.filter(
            data__date_created__range=(datetime_start, today),
            data__project=self.project
        )

        if self.entity_filter:
            entity_set = entity_set.filter(
                data__in=Data.objects.filter(entities__label=self.entity_filter))
        if self.aspect_topic:
            entity_set = entity_set.filter(
                data__in=Data.objects.filter(aspect__topic=self.aspect_topic))
        if self.aspect_name:
            entity_set = entity_set.filter(
                data__in=Data.objects.filter(aspect__label=self.aspect_name))
        if self.lang_filter and self.lang_filter[0]:
            entity_set = entity_set.filter(
                data__in=Data.objects.filter(reduce(or_, [Q(language=c)for c in self.lang_filter])))
        if self.source_filter and self.source_filter[0]:
            entity_set = entity_set.filter(
                data__in=Data.objects.filter(reduce(or_, [Q(source__label=c)for c in self.source_filter])))

        entity_count = entity_set.annotate(
            data_count=models.Count('data')).order_by('-data_count')
        entities = {"data": []}

        for ec in entity_count:
            entities["data"].append([
                ec.label,
                ', '.join(ec.classifications.values_list('label', flat=True)),
                ec.data_count
            ])
        entities['data'] = entities['data'][:5]
        return entities


class EntityTable(BaseChart):

    def render_data(self):
        # prior 7 days
        entity_set = Entity.objects.filter(
            data__date_created__range=(self.start, self.end),
            data__project=self.project
        )
        if self.entity_filter:
            entity_set = entity_set.filter(
                data__in=Data.objects.filter(entities__label=self.entity_filter))
        if self.aspect_topic:
            entity_set = entity_set.filter(
                data__in=Data.objects.filter(aspect__topic=self.aspect_topic))
        if self.aspect_name:
            entity_set = entity_set.filter(
                data__in=Data.objects.filter(aspect__label=self.aspect_name))
        if self.lang_filter and self.lang_filter[0]:
            entity_set = entity_set.filter(
                data__in=Data.objects.filter(reduce(or_, [Q(language=c)for c in self.lang_filter])))
        if self.source_filter and self.source_filter[0]:
            entity_set = entity_set.filter(
                data__in=Data.objects.filter(reduce(or_, [Q(source__label=c)for c in self.source_filter])))

        entity_count = entity_set.annotate(
            data_count=models.Count('data')).order_by('-data_count')
        entities = {"data": []}

        for ec in entity_count:
            entities["data"].append([
                ec.label,
                ', '.join(ec.classifications.values_list('label', flat=True)),
                ec.data_count
            ])

        return entities


class AdjectivesTable(BaseChart):

    def render_data(self):
        # prior 7 days
        keyword_set = Keyword.objects.filter(
            data__date_created__range=(self.start, self.end),
            data__project=self.project
        )
        if self.entity_filter:
            keyword_set = keyword_set.filter(
                data__in=Data.objects.filter(entities__label=self.entity_filter))
        if self.aspect_topic:
            keyword_set = keyword_set.filter(
                data__in=Data.objects.filter(aspect__topic=self.aspect_topic))
        if self.aspect_name:
            keyword_set = keyword_set.filter(
                data__in=Data.objects.filter(aspect__label=self.aspect_name))
        if self.lang_filter and self.lang_filter[0]:
            keyword_set = keyword_set.filter(
                data__in=Data.objects.filter(reduce(or_, [Q(language=c)for c in self.lang_filter])))
        if self.source_filter and self.source_filter[0]:
            keyword_set = keyword_set.filter(
                data__in=Data.objects.filter(reduce(or_, [Q(source__label=c)for c in self.source_filter])))

        adjective_count = keyword_set.annotate(
            data_count=models.Count('data')).order_by('-data_count')[:10]

        result = {'adjectives': []}
        print("adjectives:>", result)
        for ad in adjective_count:
            result["adjectives"].append([
                ad.label,
                ad.data_count,
            ])

        print("adjectives:>", result)
        return result


class CountriesTable(BaseChart):

    def render_data(self):
        # Show sentiment by county.
        result = {}

        result['country_labels'] = []

        positive = {'label': 'positive', 'data': [],
                    'backgroundColor': COLORS['positive']}
        negative = {'label': 'negative', 'data': [],
                    'backgroundColor': COLORS['negative']}

        for country in Country.objects.values_list('label', flat=True):
            pos_total = data_models.Data.objects.filter(
                project=self.project,
                date_created__range=(self.start, self.end), country__label=country, sentiment__gt=0).count()

            neg_total = data_models.Data.objects.filter(
                project=self.project,
                date_created__range=(self.start, self.end), country__label=country, sentiment__lt=0).count()

            if pos_total or neg_total:
                result['country_labels'].append(country)
                positive['data'].append(pos_total)
                negative['data'].append(neg_total)

        result['country_datasets'] = [positive, negative]

        return result


class Data_EntryTable(BaseChart):

    def render_data(self):

        # prior 7 days

        entry_data_set = Data.objects.filter(
            project=self.project, date_created__range=(self.start, self.end)).all()

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

        data_count = entry_data_set.order_by('-sentiment')

        def getCountry(id):
            try:
                country = str(Country.objects.get(id=id))
            except ObjectDoesNotExist:
                country = None

            return country

        entry_data = {"data": []}
        for entry in data_count.values('date_created', 'text', 'source', 'weighted_score', 'country'):
            entry_data["data"].append([
                entry['date_created'],
                entry['text'],
                str(Source.objects.get(id=entry['source'])),
                entry['weighted_score'], getCountry(entry['country']),
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

        aspect_count = aspect_set.values_list('topic').annotate(
            topic_count=Count('topic')).order_by('-topic_count')

        aspects = {"data": []}
        for topic, count in aspect_count:
            aspects["data"].append([
                topic,
                Aspect.objects.filter(topic=topic)[0].label,
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

        return {"sentiment_f_data": list(sentiment_f.values())}


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


class AspectSentimentTable(BaseChart):

    def render_data(self):

        aspect_data_set = Aspect.objects.filter(
            data__project=self.project,
            data__date_created__range=(self.start, self.end)
        )

        if self.entity_filter:
            aspect_data_set = aspect_data_set.filter(
                data__entities__label=self.entity_filter)

        if self.aspect_topic:
            aspect_data_set = aspect_data_set.filter(
                topic=self.aspect_topic)
        if self.aspect_name:
            aspect_data_set = aspect_data_set.filter(
                label=self.aspect_name)
        if self.lang_filter and self.lang_filter[0]:
            aspect_data_set = aspect_data_set.filter(
                reduce(or_, [Q(data__language=c)for c in self.lang_filter]))
        if self.source_filter and self.source_filter[0]:
            aspect_data_set = aspect_data_set.filter(
                reduce(or_, [Q(data__source__label=c)for c in self.source_filter]))

        aspect_s = aspect_data_set.values('label').annotate(
            positive=Count('sentiment', filter=Q(sentiment__gt=0)),
            negative=Count('sentiment', filter=Q(sentiment__lt=0)),
        )
        result = {'aspect_s_labels': []}
        for aspect in list(aspect_s):
            result['aspect_s_labels'].append(aspect['label'])

        positive = {'label': 'Positive', 'data': list(map(lambda d: d['positive'], list(aspect_s))),
                    'backgroundColor': COLORS['positive']}
        negative = {'label': 'Negative', 'data': list(map(lambda d: d['negative'], list(aspect_s))),
                    'backgroundColor': COLORS['negative']}
        result['aspect_s_data'] = [positive, negative]

        return result


class AspectFrequencyTable(BaseChart):

    def render_data(self):

        aspect_data_set = data_models.Aspect.objects.filter(
            data__project=self.project,
            data__date_created__range=(self.start, self.end)
        )

        if self.entity_filter:
            aspect_data_set = aspect_data_set.filter(
                data__entities__label=self.entity_filter)
        if self.aspect_topic:
            aspect_data_set = aspect_data_set.filter(
                topic=self.aspect_topic)
        if self.aspect_name:
            aspect_data_set = aspect_data_set.filter(label=self.aspect_name)
        if self.lang_filter and self.lang_filter[0]:
            aspect_data_set = aspect_data_set.filter(
                reduce(or_, [Q(data__language=c)for c in self.lang_filter]))
        if self.source_filter and self.source_filter[0]:
            aspect_data_set = aspect_data_set.filter(
                reduce(or_, [Q(data__source__label=c)for c in self.source_filter]))

        aspect_f = aspect_data_set.values('label').annotate(
            Count('label')).order_by('label')
        aspect_f_data = []

        for i, aspect in enumerate(list(aspect_f)):
            color = COLORS['contrasts'][i % (len(COLORS['contrasts'])-1)]
            aspect_f_data.append({'label': aspect['label'], 'data': [
                                 aspect['label__count']], "backgroundColor": color, "borderColor": color})
        aspect_f_data = sorted(
            aspect_f_data, key=itemgetter('data'), reverse=True)

        return {'aspect_f_data': aspect_f_data}


class AspectTimeTable(BaseChart):

    def render_data(self):
        aspect_data_set = data_models.Aspect.objects.filter(
            data__project=self.project,
            data__date_created__range=(self.start, self.end)
        )

        if self.entity_filter:
            aspect_data_set = aspect_data_set.filter(
                data__entities__label=self.entity_filter)

        if self.aspect_topic:
            aspect_data_set = aspect_data_set.filter(
                topic=self.aspect_topic)
        if self.aspect_name:
            aspect_data_set = aspect_data_set.filter(label=self.aspect_name)
        if self.lang_filter and self.lang_filter[0]:
            aspect_data_set = aspect_data_set.filter(
                reduce(or_, [Q(data__language=c)for c in self.lang_filter]))
        if self.source_filter and self.source_filter[0]:
            aspect_data_set = aspect_data_set.filter(
                reduce(or_, [Q(data__source__label=c)for c in self.source_filter]))

        result = {"aspects": {}}
        result["aspect_t_labels"] = list(
            aspect_data_set.values_list('label', flat=True).distinct())

        for aspect in result["aspect_t_labels"]:
            result["aspects"][aspect] = list(aspect_data_set.filter(label=aspect).values("label").annotate(
                Count('label')).annotate(data__date_created=F("data__date_created")).order_by("data__date_created"))

        return result


class SentimentSourceTable(BaseChart):

    def render_data(self):
        # Show sentiment by source.
        result = {}

        result['source_labels'] = []

        positive = {'label': 'positive', 'data': [],
                    'backgroundColor': COLORS['positive']}
        negative = {'label': 'negative', 'data': [],
                    'backgroundColor': COLORS['negative']}

        for label in Source.objects.values_list('label', flat=True):
            pos_total = data_models.Data.objects.filter(
                project=self.project,
                date_created__range=(self.start, self.end), source__label=label, sentiment__gt=0).count()

            neg_total = data_models.Data.objects.filter(
                project=self.project,
                date_created__range=(self.start, self.end), source__label=label, sentiment__lt=0).count()

            if pos_total or neg_total:
                result['source_labels'].append(label)
                positive['data'].append(pos_total)
                negative['data'].append(neg_total)

        result['source_datasets'] = [positive, negative]

        return result


class EmotionalEntitiesTable(BaseChart):

    def render_data(self):

        data_set = Data.objects.filter(
            project=self.project,
            date_created__range=(self.start, self.end)
        )

        if self.entity_filter:
            data_set = data_set.filter(entities__label=self.entity_filter)

        result = {}
        # Get 10 most frequent entities
        top_ten_entities = Entity.objects.filter(data__in=data_set).annotate(
            data_count=Count('data')).order_by('-data_count')[: 10]
        result['entities_for_emotions'] = [e.label for e in top_ten_entities]

        # Query 10 most frequent emotions for the entities
        top_ten_emotions = data_models.EmotionalEntity.objects.filter(
            entity__in=top_ten_entities).values('emotion__label').annotate(
            emotion_count=models.Count('emotion')).order_by('-emotion_count')[: 10]
        result['emotions'] = [e['emotion__label'] for e in top_ten_emotions]
        result['emotional_entity_data'] = []

        for index_n, entity in enumerate(result['entities_for_emotions']):
            x = list(data_models.EmotionalEntity.objects.filter(
                entity__label=entity,
                emotion__label__in=result['emotions']).values(
                    "emotion__label").annotate(
                        Count("emotion")).order_by("-emotion__count"))

            for index_m, emotion in enumerate(list(x)):
                result['emotional_entity_data'].append(
                    [index_m, index_n, emotion['emotion__count']])

        return result


CHART_LOOKUP = {
    'aspect_f': AspectFrequencyTable,
    'aspect_s': AspectSentimentTable,
    'aspect_t': AspectTimeTable,
    'aspect_table': AspectTopicTable,
    'emotional_entities': EmotionalEntitiesTable,
    'top_entity_table': TopEntityTable,
    'entity_table': EntityTable,
    'data_entrytable': Data_EntryTable,
    'adjectives_table': AdjectivesTable,
    'sentiment_f': SentimenFrequencyTable,
    'sentiment_source': SentimentSourceTable,
    'sentiment_t': SentimentTimeTable,
    'countries_t': CountriesTable,
}
