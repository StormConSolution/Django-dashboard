# -*- encoding: utf-8 -*-
from django.contrib import admin
from django.utils.safestring import mark_safe

from data.models import *

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'name')
    search_fields = ('name',)

class DataAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'text', 'source', 'language', 'sentiment')
    list_filter = ('project', 'source',)
    search_fields = ('text', 'emotionalentity__entity__label', 'emotionalentity__emotion__label',)
    readonly_fields = ('entities', 'language', 'sentiment', 'text', 'source',)
    date_hierarchy = 'date_created'

class AspectAdmin(admin.ModelAdmin):
    list_display = ('label', '_text', 'sentiment', 'topic')
    list_filter = ('label',)
    readonly_fields = ('data', 'chunk', 'topic', 'sentiment_text', 'label', 'sentiment')
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
    search_fields = ('label',)

admin.site.register(Data, DataAdmin)
admin.site.register(Aspect, AspectAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Entity, EntityAdmin)
