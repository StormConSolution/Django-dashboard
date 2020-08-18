# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.contrib import admin
from data.models import *

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'name')
    search_fields = ('name',)

class DataAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'text', 'source', 'language', 'sentiment')
    list_filter = ('project', 'source',)
    search_fields = ('text', 'emotionalentity__entity__label', 'emotionalentity__emotion__label',)
    readonly_fields = ('entities', 'language', 'sentiment', 'text', 'source',)

class AspectAdmin(admin.ModelAdmin):
    list_display = ('label', '_text', 'sentiment', 'topic')
    list_filter = ('label',)
    readonly_fields = ('data', 'chunk', 'topic', 'sentiment_text', 'label', 'sentiment')
    search_fields = ('topic', 'chunk',)

    def _text(self, obj):
        return obj.data.text
    _text.short_description = 'Text'

admin.site.register(Data, DataAdmin)
admin.site.register(Aspect, AspectAdmin)
admin.site.register(Project, ProjectAdmin)
