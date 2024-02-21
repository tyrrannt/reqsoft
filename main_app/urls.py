from django.urls import path, re_path
from . import views
from .views import get_challenge

app_name = 'main_app'

urlpatterns = [
    path('', views.index, name='index'),
    re_path(r'^acme-challenge/(?P<file_name>[\w\-]+)$', get_challenge),
]
