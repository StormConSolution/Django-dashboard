from django.db import models
from data import models as data_models
from django.db.models import Count, Q, F

from data.models import Entity, Data, Aspect, Source



class BaseChart:
    colours = [
        'rgba(255, 99, 132, 0.2)',
        'rgba(54, 162, 235, 0.2)',
        'rgba(255, 206, 86, 0.2)',
        'rgba(75, 192, 192, 0.2)',
        'rgba(153, 102, 255, 0.2)',
        'rgba(255, 159, 64, 0.2)'
    ]

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

        return {"sentiment_f_data":list(sentiment_f.values())}


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
        
        result = {'sentiment_t_labels':[]}
        for sentiment in list(sentiment_t):
            result['sentiment_t_labels'].append(sentiment['date_created'])
        date_list = list(data_set.values_list('date_created', flat=True).distinct())
        
        positive = {'label': 'Positive', 'data': list(map(lambda d: d['positive'], list(sentiment_t))),
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)'}
        negative = {'label': 'Negative', 'data': list(map(lambda d: d['negative'], list(sentiment_t))),
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)'}
        neutral = {'label': 'Neutral', 'data': list(map(lambda d: d['neutral'], list(sentiment_t))),
                   'backgroundColor': 'rgba(154, 162, 235, 0.2)'}
        result['sentiment_t_data'] = [positive,negative,neutral]
        
        return result


class AspectSentimentTable(BaseChart):


    
    def render_data(self):
        aspect_data_set = Aspect.objects.filter(
            data__project=self.project,
            data__date_created__range=(self.start, self.end)
        )

        if self.entity_filter:
            aspect_data_set = aspect_data_set.filter(
                data__entities__label=entity_filter)


        aspect_s = aspect_data_set.values('label').annotate(
            positive=Count('sentiment', filter=Q(sentiment__gt=0)),
            negative=Count('sentiment', filter=Q(sentiment__lt=0)),
            neutral=Count('sentiment', filter=Q(sentiment=0))
        )
        result = {'aspect_s_labels':[]}
        for aspect in list(aspect_s):
            result['aspect_s_labels'].append(aspect['label'])

        positive = {'label': 'Positive', 'data': list(map(lambda d: d['positive'], list(aspect_s))),
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)'}
        negative = {'label': 'Negative', 'data': list(map(lambda d: d['negative'], list(aspect_s))),
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)'}
        neutral = {'label': 'Neutral', 'data': list(map(lambda d: d['neutral'], list(aspect_s))),
                   'backgroundColor': 'rgba(154, 162, 235, 0.2)'}
        result['aspect_s_data'] = [positive,negative,neutral]
 
        return result


class AspectFrequencyTable(BaseChart):


    def render_data(self):

        aspect_data_set = data_models.Aspect.objects.filter(
            data__project=self.project,
            data__date_created__range=(self.start, self.end)
        )

        if self.entity_filter:
            aspect_data_set = aspect_data_set.filter(
                data__entities__label=entity_filter)

        aspect_f = aspect_data_set.values('label').annotate(
            Count('label')).order_by('label')
        aspect_f_data = []
        for i in list(aspect_f):
            aspect_f_data.append({'label': i['label'], 'data': [i['label__count']], "backgroundColor": 'rgba(151, 187, 205, 0.5)',
                                  "borderColor": 'rgba(151, 187, 205, 0.8)', "highlightFill": 'rgba(151, 187, 205, 0.75)', "highlightStroke": 'rgba(151, 187, 205, 1)'})
        return {'aspect_f_data':aspect_f_data}


class AspectTimeTable(BaseChart):

    def render_data(self):
        aspect_data_set = data_models.Aspect.objects.filter(
            data__project=self.project,
            data__date_created__range=(self.start, self.end)
        )

        if self.entity_filter:
            aspect_data_set = aspect_data_set.filter(
                data__entities__label=entity_filter)
        return {"aspect_t_data":[]}


class SentimentSourseTabel(BaseChart):

    def render_data(self):
        # Show sentiment by source.
        result = {}
        result['source_labels'] = list(Source.objects.values_list('label', flat=True))

        positive = {'label': 'positive', 'data': [],
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)'}
        negative = {'label': 'negative', 'data': [],
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)'}

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
        top_ten_entities = Entity.objects.filter(data__in=data_set).annotate(
            data_count=Count('data')).order_by('-data_count')
        result['entities_for_emotions'] = [e.label for e in top_ten_entities]

        top_ten_emotions = data_models.EmotionalEntity.objects.filter(entity__in=top_ten_entities).annotate(
            emotion_count=models.Count('emotion')).order_by('-emotion_count')[:10]

        emotion_count = {}
        for e in data_models.Emotion.objects.all():
            emotion_count[e.label] = data_models.EmotionalEntity.objects.filter(
                emotion=e).count()

        sorted_emotion = sorted(emotion_count.items(),
                                key=lambda item: item[1])
        result['emotions'] = [k for k, v in sorted_emotion]
        
        return result

CHART_LOOKUP = {
    'entity_table':EntityTable,
    'sentiment_f':SentimenFrequencyTable,
    'sentiment_t':SentimentTimeTable,
    'aspect_s':AspectSentimentTable,
    'aspect_f':AspectFrequencyTable,
    'aspect_t':AspectTimeTable,
    'sentiment_source':SentimentSourseTabel,
    'emotional_entities':EmotionalEntitiesTable
}