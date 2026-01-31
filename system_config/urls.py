from django.urls import path
from . import views

app_name = 'system_config'

urlpatterns = [
    path('settings/', views.settings_view, name='settings'),
]
