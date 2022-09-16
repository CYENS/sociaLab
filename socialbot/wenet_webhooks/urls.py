from django.urls import path

from . import views

app_name = 'wenet'
urlpatterns = [
    path('', views.index, name='index'),
    path('authorise_user', views.authorise_user, name='authorise_user'),
    path('create_account', views.create_account, name='create_user'),
    path('delete_account', views.delete_account, name='delete_account'),
    path('ask_question', views.ask_question, name='ask_question'),
    path('send_answer', views.send_answer, name='send_answer'),
    path('asked_questions', views.asked_questions, name='asked_questions'),
    path('mark_as_solved', views.mark_as_solved, name='mark_as_solved'),
    path('mark_as_unsolved', views.mark_as_unsolved, name='mark_as_unsolved'),
    path('question_answers', views.question_answers, name='question_answers'),
    path('available_questions', views.available_questions, name='available_questions'),
    path('messages_callback_from_wenet', views.messages_callback_from_wenet, name='messages_callback_from_wenet'),
    path('delete_question', views.delete_question, name='delete_question'),
    path('solved_questions', views.solved_questions, name='solved_questions'),
]
