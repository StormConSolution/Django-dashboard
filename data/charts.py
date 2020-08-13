from django.db import models

from data.models import Entity

class BaseChart:

    chart_type = ''

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

    chart_type = 'entity_table'

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
