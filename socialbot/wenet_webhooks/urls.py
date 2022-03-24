from django.urls import path

from . import views

app_name = 'wenet'
urlpatterns = [
    path('', views.index, name='index'),
    path('authorise_user', views.authorise_user, name='authorise_user'),
    path('create_user', views.create_user, name='create_user')
]
