# -*- encoding: utf-8 -*-
from django.urls import path  # add this

from data import api_views as views
import data.data_views as data_views

urlpatterns = [

    # Internal API calls.
    path('aspect-count/<int:project_id>/', data_views.aspect_count),
    path('aspect-topic/project/<int:project_id>/', views.aspect_topic),
    path('aspects-per-project/<int:project_id>/', data_views.aspects_per_project),
    path('classification-by-sentiment/<int:project_id>/', data_views.classification_by_sentiment),
    path('co-occurence/<int:project_id>/', views.co_occurence),
    path('csv/', data_views.csv_upload),
    path('data-item/', data_views.DataItems.as_view(), name='data-items'),
    path('data-item/<int:data_id>/', data_views.DataItem.as_view(), name='data-item'),
    path('data-per-aspect-topic/<int:project_id>/', data_views.data_per_aspect_topic),
    path('data-per-aspect/<int:project_id>/', data_views.data_per_aspect),
    path('data-per-classification-and-entity/<int:project_id>/', data_views.data_per_classification_and_entity),
    path('data-per-classification/<int:project_id>/', data_views.data_per_classification),
    path('data-per-entity/<int:project_id>/', data_views.data_per_entity),
    path('entity-aspect-for-emotion/<int:project_id>/', data_views.entity_aspect_for_emotion),
    path('entity-by-sentiment/<int:project_id>/', data_views.entity_by_sentiment),
    path('entity-classification-count/<int:project_id>/', views.entity_classification_count),
    path('export-data/', data_views.export_data),
    path('keywords/<int:project_id>/', data_views.keywords_count),
    path('most-common-chunks/<int:project_id>/', data_views.most_common_chunks),
    path('new-data/project/<int:project_id>/', data_views.data),
    path('project-overview/<int:project_id>/', views.project_overview),
    path('sentiment-per-aspect/<int:project_id>/', data_views.sentiment_per_aspect),
    path('sentiment-trend/<int:project_id>/', data_views.sentiment_trend),
    path('source-by-sentiment/<int:project_id>/', data_views.source_by_sentiment),
    path('sources-and-languages-per-project/<int:project_id>/', views.sources_languages_per_project),
    path('test-aspect-model/', data_views.aspect_model_test),
    path('test-sentiment/', data_views.sentiment_test),
    path('test/', data_views.endpoint_test),
    path('topics-per-aspect/<int:project_id>/', data_views.topics_per_aspect),
    path('volume-by-source/<int:project_id>/', views.volume_by_source),
    path('user-api-keys/', data_views.get_user_api_keys),
    path('export-comments/', data_views.export_comments_api),
    path('update-aspect-rule-weight/<int:aspect_weight_id>/', data_views.update_aspect_rule_weight),
    path('aspect-weight-scoreboard/<int:project_id>/', data_views.aspect_weights_scoreboard),
    path('search-metadata-filter-values/<int:project_id>/', data_views.search_metadata_filter_values),


    # External API calls.

    # Version without API key in the URL, but assumed to be in the header.
    path('project/', views.project_operations_with_header),
    path('data/<int:project_id>/', views.data_operations_with_header),
    path('metadata/<int:project_id>/', views.metadata_with_header),

    # Versions where API key in the URL already.
    path('project/<str:api_key>/', views.project_operations, name='project_operations'),
    path('data/<str:api_key>/<int:project_id>/', views.data_operations, name='data_operations'),
    path('metadata/<str:api_key>/<int:project_id>/', views.metadata),
]
