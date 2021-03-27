# -*- encoding: utf-8 -*-
from django.urls import path  # add this
from data import api_views as views

urlpatterns = [
    path('source/', views.SourceListAPI.as_view()),
    path('country/', views.CountryListAPI.as_view()),
    path('project/', views.ProjectListView.as_view()),
    path('data/project/<int:project_id>/', views.ProjectDataListView.as_view(), name='project-data-list'),
    path('sentiment-count/<int:project_id>/', views.sentiment_count),
    path('volume-by-source/<int:project_id>/', views.volume_by_source),
    path('co-occurence/<int:project_id>/', views.co_occurence),
    path('aspect-count/<int:project_id>/', views.aspect_count)
]
