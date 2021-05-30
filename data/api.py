# -*- encoding: utf-8 -*-
from django.urls import path  # add this
from data import api_views as views
import data.data_views as data_api_views

urlpatterns = [
    path('source/', views.SourceListAPI.as_view()),
    path('country/', views.CountryListAPI.as_view()),
    path('project/', views.ProjectListView.as_view()),
    path('data/project/<int:project_id>/', views.ProjectDataListView.as_view(), name='project-data-list'),
    path('project-overview/<int:project_id>/', views.project_overview),
    path('volume-by-source/<int:project_id>/', views.volume_by_source),
    path('source-by-sentiment/<int:project_id>/', data_api_views.source_by_sentiment),
    path('co-occurence/<int:project_id>/', views.co_occurence),
    path('sentiment-per-aspect/<int:project_id>/', data_api_views.sentiment_per_aspect),
    path('new-data/project/<int:project_id>/', data_api_views.data),
    path('export-data/', data_api_views.export_data),
    path('entity-classification-count/<int:project_id>/', views.entity_classification_count),
    path('entity-by-sentiment/<int:project_id>/', data_api_views.entity_by_sentiment),
    path('classification-by-sentiment/<int:project_id>/', data_api_views.classification_by_sentiment),
    path('data-per-classification/<int:project_id>/', data_api_views.data_per_classification),
    path('aspect-topic/project/<int:project_id>/', views.aspect_topic),
    path('sentiment-trend/<int:project_id>/', data_api_views.sentiment_trend),
    path('data-per-classification-and-entity/<int:project_id>/', data_api_views.data_per_classification_and_entity),
    path('data-per-aspect-topic/<int:project_id>/', data_api_views.data_per_aspect_topic),
    path('data-per-aspect/<int:project_id>/', data_api_views.data_per_aspect),
    path('data-per-entity/<int:project_id>/', data_api_views.data_per_entity),
    path('topics-per-aspect/<int:project_id>/', data_api_views.topics_per_aspect),
    path('entity-aspect-for-emotion/<int:project_id>/', data_api_views.entity_aspect_for_emotion),
    path('keywords/<int:project_id>/', data_api_views.keywords_count),
    path('aspect-count/<int:project_id>/', data_api_views.aspect_count),
    path('test-sentiment/', data_api_views.sentiment_test),
    path('test-aspect-model/', data_api_views.aspect_model_test),
    path('csv/', data_api_views.csv_upload),
    path('most-common-chunks/<int:project_id>/', data_api_views.most_common_chunks),
]
