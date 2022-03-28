from django.urls import path

from . import views

app_name = 'wenet'
urlpatterns = [
    path('', views.index, name='index'),
    path('authorise_user', views.authorise_user, name='authorise_user'),
    path('create_user', views.create_user, name='create_user'),
    path('ask_question', views.ask_question, name='ask_question'),
    path('send_answer', views.send_answer, name='send_answer'),
    path('asked_questions', views.asked_questions, name='asked_questions'),
    path('mark_as_solved', views.mark_as_solved, name='mark_as_solved'),
    path('question_answers', views.question_answers, name='question_answers'),
]
