import requests

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, JsonResponse

from .models import User

WENET_TOKEN_GENERATOR = 'https://wenet.u-hopper.com/dev/api/oauth2/token'
WENET_AUTHENTICATION_COMPLETE = 'http://wenet.u-hopper.com/dev/hub/frontend/oauth/complete?app_id=mH7Tbcd0W5'
WENET_SERVICES = 'https://wenet.u-hopper.com/dev/api/service'
TELEGRAM_URI = 'https://t.me/sociaLabGRCYTRCYBot?start='
APPLICATION_JSON = 'application/json'


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
    # print(request.content_params['code'])
    print(request.method)
    oauth2_request = requests.post(WENET_TOKEN_GENERATOR, data={
        'grant_type': 'authorization_code',
        'client_id' : 'mH7Tbcd0W5',
        'client_secret' : 'RkBcc8L7iRoj9iSTAQKj',
        'code' : request.GET['code']
        })
    user_tokens = oauth2_request.json()
    check_result = check_oauth2_tokens(user_tokens)
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
    u = User(id = user_details['id'], telegram_id=request.GET['user_id'],
        name= f"{user_name['first']} {user_name['last']}", language=user_details['locale'],
        access_token=user_access_token, refresh_token=user_refresh_token)
    u.save()

    
    return JsonResponse({'message' : 'user_created'})

def check_oauth2_tokens(dict: dict):
    if (dict.keys().__contains__('error')):
        return HttpResponseBadRequest()
    return None