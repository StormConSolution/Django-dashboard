# -*- encoding: utf-8 -*-
import debug_toolbar

from django.urls import path, re_path, include
from data import api_views, views

urlpatterns = [
    path('__debug__/', include(debug_toolbar.urls)),

    # The home page
    path('', views.index, name='home'),
    path('create-project/', api_views.create_project, name='create-project'),
    path('add-data/<int:project_id>/', api_views.add_data, name='add-data'),
    
    path('aspect-topics/<int:project_id>/',
         views.aspect_topics, name='aspect-topics'),
    path('aspect-topic-detail/<int:project_id>/',
         views.aspect_topic_detail, name='aspect-topic-detail'),
    path('aspect-topic-summary/<int:project_id>/',
         views.aspect_topic_summary, name='aspect-topic-summary'),

    path('entities/<int:project_id>/', views.entities, name='entities'),

    path('data-entries/<int:project_id>/',
         views.data_entries, name='data-entries'),
    #path('data-per-aspect/<int:project_id>/', views.data_per_aspect, name='data-per-aspect'),
    path('topics-per-aspect/<int:project_id>/', views.topics_per_aspect, name='topics_per_project'),
    path('projects/<int:project_id>/', views.projects, name='projects'),
    path('new-projects/', views.new_projects, name='new-projects'),
    path('new-projects/<int:project_id>/', views.new_project_details, name='new-project-details'),
    path('sentiment-per-entity/<int:project_id>/', views.sentiment_per_entity, name="sentiment-per-entity"),

    path('projects/<int:project_id>/',
         views.aspect_name, name="aspect-names"),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages')
]
