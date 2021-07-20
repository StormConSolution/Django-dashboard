from functools import reduce
import collections
from operator import or_
from operator import itemgetter
import datetime
import json

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db import connection
from django.db.models import Count, Q, F, query

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

OMITTED_LABELS = ('general', 'General',)

MAX_COMMENT_LENGTH = 200

class BaseChart:

    def __init__(self, project, start, end, entity_filter, 
            aspect_topic, aspect_name, lang_filter, source_filter, request):

        self.aspect_name = aspect_name
        self.aspect_topic = aspect_topic
        self.end = end
        self.entity_filter = entity_filter
        self.lang_filter = lang_filter
        self.project = project
        self.source_filter = source_filter
        self.start = start
        
        # These get used by the server side data tables.
        self.page_size = int(request.GET.get('length', 0))
        self.offset = int(request.GET.get('start', 0))
        self.draw = int(request.GET.get('draw', 0))
        self.search = request.GET.get('search[value]', '')

    def render_data(self):
        """
        Returns the data necessary to render a chart in JavaScript.
        """
        raise NotImplementedError
    

class AspectCooccurrence(BaseChart):
    """
    Generate the data needed for a co-occurrence heat map.
    """
    def render_data(self):

        UNIQUE_ASPECTS_QUERY = """
            SELECT distinct data_aspect.label
            FROM data_aspect, data_data
            WHERE data_aspect.data_id = data_data.id AND
            data_data.project_id = %s AND
            data_aspect.label != 'General' AND
            data_aspect.label != 'general' AND
            data_data.date_created between %s AND %s
        """
        aspect_labels = []
        with connection.cursor() as cursor:
            cursor.execute(UNIQUE_ASPECTS_QUERY, (self.project.id, self.start, self.end,))
            for row in cursor.fetchall():
                aspect_labels.append(row[0])
        
        ASPECT_QUERY = """ 
            SELECT * 
            FROM get_aspect_label_percentages(%s , $SQL$ date_created between %s AND %s $SQL$) 
            ORDER BY label1, label2;
        """

        ASPECT_QUERY_WITH_WHERE_CLAUSE = """ 
            SELECT * 
            FROM get_aspect_label_percentages(%s , $SQL$ date_created between %s AND %s and {} $SQL$) 
            ORDER BY label1, label2;
        """

        query_args = [self.project.id, self.start, self.end]

        where_clause = []
        if self.lang_filter:
            where_clause.append("language IN ('{}')".format("','".join(self.lang_filter)))
        
        if self.source_filter:
            where_clause.append('source_id IN ({})'.format(",".join(self.source_filter)))
    
        series_data = []
        s = {}
        handled = {}
        with connection.cursor() as cursor:

            try:
                if where_clause:
                    cursor.execute(ASPECT_QUERY_WITH_WHERE_CLAUSE.format(' AND '.join(where_clause)), query_args)
                else:
                    cursor.execute(ASPECT_QUERY, query_args)
            except Exception as e:
                # TODO: If this data for this project hasn't been calculated, this
                # function errors out. Needs to be fixed.
                return {
                    'aspect_cooccurrence_data':[],
                }

            for row in cursor.fetchall():
                l1, l2, percent, = row
                if l1 in OMITTED_LABELS or l2 in OMITTED_LABELS:
                    continue
                if not handled.get(l1):
                    if s:
                        series_data.append(s)
                    s = {'name':l1, 'data':[]}
                    handled[l1] = True
                s['data'].append({'x':l2, 'y':float(percent)})
            
        # Append the last one in our loop.
        if s:
            series_data.append(s)

        # Not all aspects might be present so go through the series and make
        # sure all data is padded out.
        if len(series_data) != len(aspect_labels):
            empty_row = [{'x':l, 'y':0} for l in aspect_labels]

            for idx, label in enumerate(aspect_labels):
                if len(series_data) <= idx:
                    series_data.insert(idx, {'name':label, 'data':empty_row})
                elif series_data[idx]['name'] != label:
                    series_data.insert(idx, {'name':label, 'data':empty_row})
        
        return {
            'aspect_cooccurrence_data':series_data,
        }
