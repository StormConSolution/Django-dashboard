# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.urls import path, include  # add this

admin.site.site_header = "Repustate Admin"
admin.site.site_title = "Repustate Admin"
admin.site.index_title = "Welcome to Repustate"

urlpatterns = [
    path('admin/', admin.site.urls),          # Django admin route
    path("", include("authentication.urls")),  # Auth routes - login / register
    path("", include("data.urls"))             # UI Kits Html files
]
