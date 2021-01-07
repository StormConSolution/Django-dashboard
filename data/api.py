# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path  # add this
from data import views


urlpatterns = [
    path('source/', views.SourceListAPI.as_view()),
    path('country/', views.CountryListAPI.as_view()),
    path('project/', views.ProjectListView.as_view()),
    path('data/project/<int:project_id>/', views.ProjectDataListView.as_view(), name='project-data-list')
]
