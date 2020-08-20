# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from data import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('projects/<int:project_id>/', views.projects, name='projects'),
    
    path('entities/<int:project_id>/', views.entities, name='entities'),
    
    path('aspect-topics/<int:project_id>/', views.aspect_topics, name='aspect-topics'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
