# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.contrib import admin
from data.models import *

class DataAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'text', 'source', 'language', 'sentiment')
    list_filter = ('source',)
    search_fields = ('text', 'emotionalentity__entity__label', 'emotionalentity__emotion__label',)
    readonly_fields = ('entities', 'language', 'sentiment', 'text', 'source',)

class AspectAdmin(admin.ModelAdmin):
    list_display = ('label', 'sentiment', 'topic')
    list_filter = ('label',)
    readonly_fields = ('data', 'chunk', 'topic', 'sentiment_text', 'label', 'sentiment')
    search_fields = ('topic', 'chunk',)

admin.site.register(Data, DataAdmin)
admin.site.register(Aspect, AspectAdmin)
