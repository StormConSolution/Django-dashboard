# -*- encoding: utf-8 -*-
import datetime

from django.contrib import admin
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.text import slugify

import unicodecsv

from data.models import *

# Action for exporting a queryset.


def export_selected_objects(modeladmin, request, queryset):

    model = queryset.model
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % slugify(
        model.__name__)
    writer = unicodecsv.writer(response, encoding='utf-8')

    # Write headers to CSV file
    headers = []
    for field in model._meta.fields:
        headers.append(field.verbose_name.title())

    writer.writerow(headers)

    # Write data to CSV file
    for obj in queryset:
        row = []
        for field in model._meta.fields:
            try:
                val = getattr(obj, field.name, None)
            except:
                row.append('')
                continue
            if callable(val):
                val = val()
            if isinstance(val, datetime.datetime):
                row.append(val.strftime('%m-%d-%Y'))
            else:
                row.append(val)
        writer.writerow(row)
    return response


export_selected_objects.short_description = 'Export search results'
admin.site.add_action(export_selected_objects)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'name', 'aspect_model',)
    search_fields = ('name',)


class DataAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'text', 'source', 'language', 'sentiment')
    list_filter = ('project', 'source', 'language')
    raw_id_fields = ('project',)
    search_fields = ('text',)
    readonly_fields = ('entities', 'language', 'sentiment', 'text', 'source', 'country', 'keywords',)
    date_hierarchy = 'date_created'


class AspectAdmin(admin.ModelAdmin):
    list_display = ('label', '_text', 'sentiment', 'topic')
    list_filter = ('label', 'data__project')
    readonly_fields = ('data', 'chunk', 'topic',
                       'sentiment_text', 'label', 'sentiment')
    search_fields = ('topic', 'chunk',)

    def _text(self, obj):
        return obj.data.text
    _text.short_description = 'Text'


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', '_data_count', '_view')
    filter_horizontal = ('users', 'charts')

    def _view(self, obj):
        return mark_safe('<a href="{0}">{1}</a>'.format(
            obj.get_absolute_url(),
            ("View on site"))
        )
    _view.allow_tags = True
    _view.short_description = "View on site"

    def _data_count(self, obj):
        return obj.data_set.count()
    _data_count.short_description = 'Data'


class EntityAdmin(admin.ModelAdmin):
    list_display = ('label',)
    search_fields = ('label', 'classifications__label')
    filter_horizontal = ('classifications',)


class TwitterSearchAdmin(admin.ModelAdmin):
    list_display = ('query', 'project_name', 'status',)


admin.site.register(Data, DataAdmin)
admin.site.register(Aspect, AspectAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(ChartType)
admin.site.register(TwitterSearch, TwitterSearchAdmin)
admin.site.register(AspectModel)
admin.site.register(Keyword)
admin.site.register(Country)
