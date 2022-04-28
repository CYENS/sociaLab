import requests
import os
import time

from telegram import Bot, Update

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseNotFound, JsonResponse

from .models import User, Question, Answer

BOT_TOKEN = '5190722737:AAHrk9MCT01h646wPP9G5M2qjOYm3fiRYtw'

APP_ID = os.environ['APP_ID']
APP_SECRET = os.environ['APP_SECRET']
TASK_TYPE_ID = '625036454ff70359a68b8db8'
WENET_TOKEN_GENERATOR = os.environ['WENET_TOKEN_GENERATOR']
WENET_AUTHENTICATION_COMPLETE = os.environ['WENET_AUTHENTICATION_COMPLETE']
WENET_SERVICES = os.environ['WENET_SERVICES']
TELEGRAM_URI = os.environ['TELEGRAM_URI']
APPLICATION_JSON = 'application/json'

@csrf_exempt
def messages_callback_from_wenet(request: HttpRequest):
    if request.method == 'POST':
        print(request.POST.get('attributes').get('message'))
    return HttpResponse("")

def _check_oauth2_tokens(dict: dict):
    if (dict.keys().__contains__('error')):
        return HttpResponseBadRequest()
    return None

def _question_checks(user: User, question_id_field):
    try:
        question: Question = Question.objects.get(id=question_id_field)
    except Question.DoesNotExist:
        return HttpResponseNotFound()

    if (question.user == user):
        return question
    else:
        return HttpResponseNotAllowed()

def _update_user_token(user: User):
    """
    
    Used to create a new access refresh token pair for the user to keep using the app."""
    oauth2_request = requests.post(WENET_TOKEN_GENERATOR, data={
        'grant_type' : 'refresh_token',
        'client_id' : APP_ID,
        'client_secret' : APP_SECRET,
        'code' : user.refresh_token
    }).json()
    user.access_token = oauth2_request['access_token']
    user.refresh_token = oauth2_request['refresh_token']
    user.save()

# def _translate(user: User, message: str):
#     json = {
#         user.language : message,
#         'en' : english_translation,
#         transtated_language : other_language_translation,
#     }

# Create your views here.

def index(request: HttpRequest):
    return HttpResponse("WeNet webhooks")

def authorise_user(request: HttpRequest):
    return redirect(f"{TELEGRAM_URI}{request.GET['code']}")

@csrf_exempt
def create_user(request: HttpRequest):
    oauth2_request = requests.post(WENET_TOKEN_GENERATOR, data={
        'grant_type': 'authorization_code',
        'client_id' : APP_ID,
        'client_secret' : APP_SECRET,
        'code' : request.POST['code']
    })
    user_tokens = oauth2_request.json()
    check_result = _check_oauth2_tokens(user_tokens)
    if (check_result is not None):
        return check_result

    user_access_token = user_tokens['access_token']
    user_refresh_token = user_tokens['refresh_token']
    HEADERS = {
        'Authorization' : user_access_token,
        'Accept' : APPLICATION_JSON
    }
    user_profile_id = requests.get(f'{WENET_SERVICES}/token', headers=HEADERS).json()['profileId']
    user_details_request = requests.get(f'{WENET_SERVICES}/user/profile/{user_profile_id}', headers=HEADERS)
    user_details = user_details_request.json()
    user_name = user_details['name']
    u = User(id = user_details['id'], telegram_id=request.POST['user_id'],
        name= f"{user_name['first']} {user_name['last']}", language=user_details['locale'],
        access_token=user_access_token, refresh_token=user_refresh_token)
    u.save()
    
    return JsonResponse({'message' : 'user_created'})

@csrf_exempt
def ask_question(request: HttpRequest):
    user_id = request.POST['user_id']
    message = request.POST['question']

    user: User = User.objects.get(telegram_id=user_id)

    question = Question(user=user, question_text={user.language : message})

    question.save()

    return HttpResponse()

def test(request: HttpRequest):
    bot = Bot(BOT_TOKEN)
    bot.send_message(chat_id=5096066075, text= 'Test')
    return HttpResponse()

def create_wenet_question(user: User, question: Question):
    HEADERS = {
        'Authorization': user.access_token,
        'Accept': APPLICATION_JSON
    }
    DATA = {
        'appId': APP_ID,
        'requesterId': user.id,
        'goal': {
            'name': question.question_text
        },
        'taskTypeId': TASK_TYPE_ID
    }
    
    request = requests.post(f'{WENET_SERVICES}/task', headers=HEADERS, json=DATA)

    if (request.status_code != 200):
        _update_user_token(user)
        HEADERS['Authorization'] = user.access_token
        request = requests.post(f'{WENET_SERVICES}/task', headers=HEADERS, json=DATA)

    wenet_question_id = request.json().get('id')
    return wenet_question_id

def create_wenet_answer(user: User, question: Question):
    HEADERS = {
        'Authorization': user.access_token,
        'Accept': 'application/json'
    }
    DATA = {
        'taskId': '62540bf64ff70359a68b8dbc', #add the question task id to the question model
        'label': 'AnswerQuestion',
        'attributes': {
            'message': question.question_text
        },
        'actioneerId': str(user.id),
        "_creationTs": int(time.time()*1000.0),
        "_lastUpdateTs": int(time.time()*1000.0),

    }
    responce = requests.post(f'{WENET_SERVICES}/task/transaction', headers=HEADERS, json=DATA).status_code
    return responce

@csrf_exempt
def send_answer(request: HttpRequest):
    user_id = request.POST['user_id']
    question_id = request.POST['question_id']
    message = request.POST['answer']

    user: User = User.objects.get(telegram_id=user_id)
    question: Question = Question.objects.get(id=question_id)

    answer = Answer(user=user, question=question, answer_text={user.language : message})
    answer.save()

    return HttpResponse()

def asked_questions(request: HttpRequest):
    user_id = request.GET['user_id']
    user: User = User.objects.get(telegram_id=user_id)
    questions = Question.objects.filter(user=user)
    
    result = []

    for question in questions:
        result.append({
            'id' : question.id,
            'text' : question.question_text[user.language]
        })

    return JsonResponse({'questions' : result})

@csrf_exempt
def mark_as_solved(request: HttpRequest):
    user: User = User.objects.get(telegram_id=request.POST['user_id'])
    result = _question_checks(user, request.POST['question_id'])

    if (isinstance(result, Question)):
        result.save()
        return HttpResponse()
    else:
        return result

def question_answers(request: HttpRequest):
    user: User = User.objects.get(telegram_id=request.GET['user_id'])
    result = _question_checks(user, request.GET['question_id'])

    if (isinstance(result, Question)):
        answers = result.answer_set.all()
        result = []
        for answer in answers:
            result.append({
                'id' : answer.id,
                'text' : answer.answer_text[user.language]
            })
        return JsonResponse({'answers' : result})
    else:
        return result