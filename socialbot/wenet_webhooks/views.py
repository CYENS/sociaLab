import requests

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseNotFound, JsonResponse

from .models import User, Question, Answer

WENET_TOKEN_GENERATOR = 'https://wenet.u-hopper.com/dev/api/oauth2/token'
WENET_AUTHENTICATION_COMPLETE = 'http://wenet.u-hopper.com/dev/hub/frontend/oauth/complete?app_id=mH7Tbcd0W5'
WENET_SERVICES = 'https://wenet.u-hopper.com/dev/api/service'
TELEGRAM_URI = 'https://t.me/sociaLabGRCYTRCYBot?start='
APPLICATION_JSON = 'application/json'

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

# Create your views here.

def index(request: HttpRequest):
    return HttpResponse("WeNet webhooks")

def authorise_user(request: HttpRequest):
    return redirect(f"{TELEGRAM_URI}{request.GET['code']}")

def update_user_token(user: User):
    """
    
    Used to create a new access refresh token pair for the user to keep using the app."""
    oauth2_request = requests.post(WENET_TOKEN_GENERATOR, data={
        'grant_type' : 'refresh_token',
        'client_id' : 'mH7Tbcd0W5',
        'client_secret' : 'RkBcc8L7iRoj9iSTAQKj',
        'code' : user.refresh_token
    }).json()
    user.access_token = oauth2_request['access_token']
    user.refresh_token = oauth2_request['refresh_token']
    user.save()

@csrf_exempt
def create_user(request: HttpRequest):
    oauth2_request = requests.post(WENET_TOKEN_GENERATOR, data={
        'grant_type': 'authorization_code',
        'client_id' : 'mH7Tbcd0W5',
        'client_secret' : 'RkBcc8L7iRoj9iSTAQKj',
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
        'Accept' : 'application/json'
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
            'text' : question.question_text[user.language]})

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
                'text' : answer.answer_text[user.language]})
        return JsonResponse({'answers' : result})
    else:
        return result