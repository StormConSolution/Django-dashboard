# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from rest_framework import routers
from django.urls import path, include  # add this
from data import views


router = routers.DefaultRouter()
router.register(r'source', views.SourceViewSet)
router.register(r'country', views.CountryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('project/', views.ProjectListView.as_view()),
    path('data/project/<int:project_id>/', views.ProjectDataListView.as_view(), name='project-data-list')
]
