# -*- encoding: utf-8 -*-

from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "Repustate IQ Admin"
admin.site.site_title = "Repustate IQ Admin"
admin.site.index_title = "Welcome to Repustate IQ"

urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + [
    path('admin/', admin.site.urls, name="admin"),  # Django admin route
    path("api/", include("data.api_urls")),  # API Urls
    path("", include("authentication.urls")),  # Auth routes - login / register

    path("", include("data.urls"))  # UI Kits Html files

] 
