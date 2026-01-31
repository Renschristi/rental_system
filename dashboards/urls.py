"""
Dashboards URL Configuration
"""
from django.urls import path
from . import views

app_name = 'dashboards'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('analytics/', views.analytics_view, name='analytics'),
]
