# -*- encoding: utf-8 -*-
from django.urls import path  # add this

from data import api_views as views
import data.data_views as data_api_views

urlpatterns = [

    # Internal API calls.
    path('aspect-count/<int:project_id>/', data_api_views.aspect_count),
    path('aspect-topic/project/<int:project_id>/', views.aspect_topic),
    path('aspects-per-project/<int:project_id>/', data_api_views.aspects_per_project),
    path('classification-by-sentiment/<int:project_id>/', data_api_views.classification_by_sentiment),
    path('co-occurence/<int:project_id>/', views.co_occurence),
    path('csv/', data_api_views.csv_upload),
    path('data-per-aspect-topic/<int:project_id>/', data_api_views.data_per_aspect_topic),
    path('data-per-aspect/<int:project_id>/', data_api_views.data_per_aspect),
    path('data-per-classification-and-entity/<int:project_id>/', data_api_views.data_per_classification_and_entity),
    path('data-per-classification/<int:project_id>/', data_api_views.data_per_classification),
    path('data-per-entity/<int:project_id>/', data_api_views.data_per_entity),
    path('entity-aspect-for-emotion/<int:project_id>/', data_api_views.entity_aspect_for_emotion),
    path('entity-by-sentiment/<int:project_id>/', data_api_views.entity_by_sentiment),
    path('entity-classification-count/<int:project_id>/', views.entity_classification_count),
    path('export-data/', data_api_views.export_data),
    path('keywords/<int:project_id>/', data_api_views.keywords_count),
    path('most-common-chunks/<int:project_id>/', data_api_views.most_common_chunks),
    path('new-data/project/<int:project_id>/', data_api_views.data),
    path('project-overview/<int:project_id>/', views.project_overview),
    path('sentiment-per-aspect/<int:project_id>/', data_api_views.sentiment_per_aspect),
    path('sentiment-trend/<int:project_id>/', data_api_views.sentiment_trend),
    path('source-by-sentiment/<int:project_id>/', data_api_views.source_by_sentiment),
    path('sources-and-languages-per-project/<int:project_id>/', views.sources_languages_per_project),
    path('test-aspect-model/', data_api_views.aspect_model_test),
    path('test-sentiment/', data_api_views.sentiment_test),
    path('test/', data_api_views.endpoint_test),
    path('topics-per-aspect/<int:project_id>/', data_api_views.topics_per_aspect),
    path('volume-by-source/<int:project_id>/', views.volume_by_source),
    path('user-api-keys/', data_api_views.get_user_api_keys),
   
    # External API calls.
    path('project/<str:api_key>/', views.project_operations, name='project_operations'),
    path('data/<str:api_key>/<int:project_id>/', views.data_operations, name='data_operations'),
]
