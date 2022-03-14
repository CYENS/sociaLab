from django.urls import path

from . import views

app_name = 'wenet'
urlpatterns = [
    path('', views.index, name='index'),
]
