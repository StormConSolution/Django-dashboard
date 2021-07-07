# -*- encoding: utf-8 -*-
import debug_toolbar

from django.urls import path, re_path, include
from data import api_views, views

urlpatterns = [
    path('__debug__/', include(debug_toolbar.urls)),

    # The home page
    path('', views.index, name='index'),
    path('project/', views.Projects.as_view(), name='project'),
    path('create-project/', api_views.create_project, name='create-project'),
    path('add-data/<int:project_id>/', api_views.add_data, name='add-data'),
    path('alert/toggle/<int:aspect_rule_id>/', views.alert_rule_toggle, name='alert-rule-toggle'),
    
    path('topics-per-aspect/<int:project_id>/', views.topics_per_aspect, name='topics_per_project'),
    path('project/<int:project_id>/', views.new_project_details, name='project'),
    path('delete-project/<int:project_id>/', views.delete_project_details, name='delete-project'),
    
    path('aspect/', views.AspectsList.as_view(), name='aspects'),
    path('aspect/<int:aspect_id>/', views.Aspect.as_view(), name='aspect'),

    path('entity/', views.EntitiesList.as_view(), name='entities'),
    path('entity/<int:entity_id>/', views.Entity.as_view(), name='entity'),

    path('sentiment/', views.SentimentList.as_view(), name='sentiment'),
    path('sentiment/<int:sentiment_id>/', views.Sentiment.as_view(), name='sentiment'),
    path('sentiment-per-entity/<int:project_id>/', views.sentiment_per_entity, name="sentiment-per-entity"),

    path('alerts/', views.AlertRuleList.as_view(), name='alerts'),
    path('alerts/<int:alert_id>/', views.AlertRule.as_view(), name='alerts'),

    path('support/', views.support, name='support'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages')
]
