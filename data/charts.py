from django.db import models
from data import models as data_models
from django.db.models import Count, Q, F

from data.models import Entity, Data, Aspect, Source

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
    'positive': 'rgba(60, 180, 75,0.5)',
    'negative': 'rgba(230, 25, 75,0.5)',
    'neutral': 'rgba(67, 99, 216,0.5)',
    'contrasts': DEFAULT_COLORS
}

class BaseChart:
    
    def __init__(self, project, start, end, entity_filter):
        self.project = project
        self.start = start
        self.end = end
        self.entity_filter = entity_filter

    def render_data(self):
        """
        Returns the data necessary to render a chart in JavaScript.
        """
        raise NotImplementedError


class EntityTable(BaseChart):

    def render_data(self):
        entity_set = Entity.objects.filter(
            data__date_created__range=(self.start, self.end),
            data__project=self.project
        )
        if self.entity_filter:
            entity_set = entity_set.filter(
                data__in=Data.objects.filter(entities__label=self.entity_filter))

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

class AspectTopicTable(BaseChart):

    def render_data(self):
        aspect_set = Aspect.objects.filter(
            data__date_created__range=(self.start, self.end),
            data__project=self.project
        )
        if self.entity_filter:
            aspect_set = aspect_set.filter(
                data__in=Data.objects.filter(entities__label=self.entity_filter))

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

class SentimenFrequencyTable(BaseChart):
    
    def render_data(self):
        data_set = Data.objects.filter(
            project=self.project,
            date_created__range=(self.start, self.end)
        )

        if self.entity_filter:
            data_set = data_set.filter(entities__label=self.entity_filter)

        sentiment_f = data_set.aggregate(
            positive=models.Count('sentiment', filter=Q(sentiment__gt=0)),
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

        sentiment_t = data_set.values('date_created').annotate(
            positive=Count('sentiment', filter=Q(sentiment__gt=0)),
            negative=Count('sentiment', filter=Q(sentiment__lt=0)),
            neutral=Count('sentiment', filter=Q(sentiment=0))
        ).order_by('date_created')

        result = {'sentiment_t_labels': []}
        for sentiment in list(sentiment_t):
            result['sentiment_t_labels'].append(sentiment['date_created'])

        positive = {'label': 'Positive', 'data': list(map(lambda d: d['positive'], list(sentiment_t))),
                    'backgroundColor': COLORS['positive'], 'borderColor': COLORS['positive'], "fill": False, }
        negative = {'label': 'Negative', 'data': list(map(lambda d: d['negative'], list(sentiment_t))),
                    'backgroundColor': COLORS['negative'], 'borderColor': COLORS['negative'], "fill": False}
        neutral = {'label': 'Neutral', 'data': list(map(lambda d: d['neutral'], list(sentiment_t))),
                   'backgroundColor': COLORS['neutral'], 'borderColor': COLORS['neutral'], "fill": False}
        result['sentiment_t_data'] = [positive, negative, neutral]

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

        aspect_s = aspect_data_set.values('label').annotate(
            positive=Count('sentiment', filter=Q(sentiment__gt=0)),
            negative=Count('sentiment', filter=Q(sentiment__lt=0)),
            neutral=Count('sentiment', filter=Q(sentiment=0))
        )
        result = {'aspect_s_labels': []}
        for aspect in list(aspect_s):
            result['aspect_s_labels'].append(aspect['label'])

        positive = {'label': 'Positive', 'data': list(map(lambda d: d['positive'], list(aspect_s))),
                    'backgroundColor': COLORS['positive']}
        negative = {'label': 'Negative', 'data': list(map(lambda d: d['negative'], list(aspect_s))),
                    'backgroundColor': COLORS['negative']}
        neutral = {'label': 'Neutral', 'data': list(map(lambda d: d['neutral'], list(aspect_s))),
                   'backgroundColor': COLORS['neutral']}
        result['aspect_s_data'] = [positive, negative, neutral]

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
        result = {"aspects": {}}
        result["aspect_t_labels"] = list(
            aspect_data_set.values_list('label', flat=True).distinct())

        for aspect in result["aspect_t_labels"]:
            result["aspects"][aspect] = list(aspect_data_set.filter(label=aspect).values("label").annotate(
                Count('label')).annotate(data__date_created=F("data__date_created")).order_by("data__date_created"))

        return result


class SentimentSourseTable(BaseChart):

    def render_data(self):
        # Show sentiment by source.
        result = {}
        result['source_labels'] = list(
            Source.objects.values_list('label', flat=True))

        positive = {'label': 'positive', 'data': [],
                    'backgroundColor': COLORS['positive']}
        negative = {'label': 'negative', 'data': [],
                    'backgroundColor': COLORS['negative']}

        for label in result['source_labels']:
            positive['data'].append(data_models.Data.objects.filter(
                date_created__range=(self.start, self.end), source__label=label, sentiment__gt=0).count())

            negative['data'].append(data_models.Data.objects.filter(
                date_created__range=(self.start, self.end), source__label=label, sentiment__lt=0).count())
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
            data_count=Count('data')).order_by('-data_count')[:10]
        result['entities_for_emotions'] = [e.label for e in top_ten_entities]

        # Query 10 most frequent emotions for the entities
        top_ten_emotions = data_models.EmotionalEntity.objects.filter(
                entity__in=top_ten_entities).values('emotion__label').annotate(
            emotion_count=models.Count('emotion')).order_by('-emotion_count')[:10]
        result['emotions'] = [e['emotion__label'] for e in top_ten_emotions]
        result['emotional_entity_data'] = []
        
        for index_n, entity in enumerate(result['entities_for_emotions']):
            x = list(data_models.EmotionalEntity.objects.filter(
                entity__label=entity,
                emotion__label__in=result['emotions']).values(
                    "emotion__label").annotate(
                        Count("emotion")).order_by("-emotion__count"))
            
            for index_m, emotion in enumerate(list(x)):
                result['emotional_entity_data'].append([index_m, index_n, emotion['emotion__count']])

        return result


CHART_LOOKUP = {
    'aspect_f':AspectFrequencyTable,
    'aspect_s':AspectSentimentTable,
    'aspect_t':AspectTimeTable,
    'aspect_table':AspectTopicTable,
    'emotional_entities':EmotionalEntitiesTable,
    'entity_table':EntityTable,
    'sentiment_f':SentimenFrequencyTable,
    'sentiment_source':SentimentSourseTable,
    'sentiment_t':SentimentTimeTable,
}