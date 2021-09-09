# -*- encoding: utf-8 -*-
import codecs
import datetime

from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.text import slugify

import unicodecsv

from data.models import *
from dashboard import tasks

# Action for exporting a queryset.
def export_selected_objects(modeladmin, request, queryset):

    model = queryset.model
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % slugify(model.__name__)
    response.write(codecs.BOM_UTF8)

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

def make_positive(modeladmin, request, queryset):
    """
    Set sentiment to positive.
    """
    queryset.update(sentiment=0.775)
    Aspect.objects.filter(data__in=queryset, sentiment__lt=0).update(sentiment=0.755)
    
    messages.add_message(request, messages.SUCCESS, 'Positive sentiment has been set.')

def make_negative(modeladmin, request, queryset):
    """
    Set sentiment to negative.
    """
    queryset.update(sentiment=-0.775)
    Aspect.objects.filter(data__in=queryset, sentiment__gt=0).update(sentiment=-0.755)

    messages.add_message(request, messages.SUCCESS, 'Negative sentiment has been set.')

class DataAdmin(admin.ModelAdmin):
    actions = (make_positive, make_negative,)
    list_display = ('date_created', 'project', 'text', 'source', 'language', 'sentiment')
    list_filter = ('project', 'language', 'project__aspect_model')
    raw_id_fields = ('project',)
    search_fields = ('text', 'url')
    readonly_fields = ('entities', 'language', 'text', 'source', 'country', 'metadata')
    date_hierarchy = 'date_created'

class AspectAdmin(admin.ModelAdmin):
    list_display = ('label', 'chunk', 'sentiment', 'topic')
    list_filter = ('label', 'data__project')
    readonly_fields = ('data', 'chunk', 'topic', 'sentiment_text', 'label')
    search_fields = ('topic', 'chunk',)

class AspectModelAdmin(admin.ModelAdmin):
    list_display = ('label', 'standard', 'managed', 'language')
    list_filter = ('standard', 'language', 'managed')
    filter_horizontal = ('users',)

class AspectRuleAdmin(admin.ModelAdmin):
    list_display = ('rule_name', 'aspect_model', 'definition')
    list_filter = ('aspect_model',)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_created', '_aspect_model', '_data_count', '_view')
    filter_horizontal = ('users',)
    search_fields = ('name', 'users__email')
    fieldsets = (
        (None, {
            'fields':('name', 'aspect_model', 'users', 'geo_enabled', 
                "api_key", "popup_title", "popup_text"),
        }),
    )

    def _aspect_model(self, obj):
        if not obj.aspect_model:
            return ''
        elif obj.aspect_model.standard:
            return obj.aspect_model.label
        else:
            return mark_safe('<a href="/admin/data/aspectrule/?aspect_model__id={0}">{1}</a>'.format(
                obj.aspect_model.id, obj.aspect_model.label))
    _aspect_model.allow_tags = True
    _aspect_model.short_description = "Aspect model"

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
    list_filter = ('data__project',)
    filter_horizontal = ('classifications',)


class TwitterSearchAdmin(admin.ModelAdmin):
    list_display = ('query', 'project_name', 'status', 'created_by',)
    
    fieldsets = (
        (None, {
            'fields':('query', 'project_name', 'aspect', 'status'),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super(TwitterSearchAdmin, self).save_model(request, obj, form, change)
        if not change:
            # New request for twitter.
            tasks.process_twitter_search.delay(obj.id)

class SummaryAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'project', )
    raw_id_fields = ('project',)

class AlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'project', )
    raw_id_fields = ('project', 'data',)

class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'aspect', 'frequency', 'period', 'active')
    raw_id_fields = ('project',)

class SourceAdmin(admin.ModelAdmin):
    search_fields = ('label',)

class PredefinedAspectRuleAdmin(admin.ModelAdmin):
    list_display = ("label",)

class ExportCommentsAdmin(admin.ModelAdmin):
    list_display = ('guid', 'project', 'source', 'url')

admin.site.register(Data, DataAdmin)
admin.site.register(Aspect, AspectAdmin)
admin.site.register(AspectRule, AspectRuleAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(ChartType)
admin.site.register(TwitterSearch, TwitterSearchAdmin)
admin.site.register(AspectModel, AspectModelAdmin)
admin.site.register(Country)
admin.site.register(Source, SourceAdmin)
admin.site.register(Summary, SummaryAdmin)
admin.site.register(Alert, AlertAdmin)
admin.site.register(AlertRule, AlertRuleAdmin)
admin.site.register(PredefinedAspectRule, PredefinedAspectRuleAdmin)
admin.site.register(ExportComments, ExportCommentsAdmin)
