# -*- encoding: utf-8 -*-

from django.contrib import admin
from django.urls import path, include  # add this
from rest_framework import routers

from data import views

admin.site.site_header = "Repustate Admin"
admin.site.site_title = "Repustate Admin"
admin.site.index_title = "Welcome to Repustate"

router = routers.DefaultRouter()
router.register('data', views.DataViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),          # Django admin route
    path('api/', include(router.urls)),
    path("", include("authentication.urls")),  # Auth routes - login / register
    path("", include("data.urls"))             # UI Kits Html files
]
