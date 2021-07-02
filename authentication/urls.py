# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, include
from .views import login_view, register_user, guest_login, firebase_login, firebase_login_api, firebase_logout, logout_view
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", logout_view, name="logout"),
    path("firebase-logout/", firebase_logout, name="firebase-logout"),
    path("guest/", guest_login, name="guest-login"),
    path("firebase-login/", firebase_login, name="firebase-login"),
    path("firebase-login-api/", firebase_login_api, name="firebase-login-api"),

]
