from django.contrib import admin

from customize.models import *

class SettingAdmin(admin.ModelAdmin):
    filter_horizontal = ('users',)

admin.site.register(Setting, SettingAdmin)
