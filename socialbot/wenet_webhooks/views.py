import string
import requests
import os
import time
import json
import random

from threading import Thread
from googletrans import Translator
from telegram import Bot, ParseMode, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater,CommandHandler, MessageHandler, Filters

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseNotFound, JsonResponse
import logging
from .models import User, Question, Answer, Best_Answer, Answer_Feedback

BOT_TOKEN = os.environ['BOT_TOKEN']

APP_ID = os.environ['APP_ID']
APP_SECRET = os.environ['APP_SECRET']
TASK_TYPE_ID = '625036454ff70359a68b8db8'
WENET_TOKEN_GENERATOR = os.environ['WENET_TOKEN_GENERATOR']
WENET_AUTHENTICATION_COMPLETE = os.environ['WENET_AUTHENTICATION_COMPLETE']
WENET_SERVICES = os.environ['WENET_SERVICES']
TELEGRAM_URI = os.environ['TELEGRAM_URI']
APPLICATION_JSON = 'application/json'
logger = logging.getLogger(__name__)

@csrf_exempt
# FIXME This, does not work. Maybe we need to create our own "callback" function.
def messages_callback_from_wenet(request: HttpRequest):
    """
    Callback function which wenet should use.
    """
    # if request.method == 'POST':
    #     data = json.loads(request.body)
    #     message_type = data.get('label')
    #     user_id = data.get('receiverId')
    #     app_id = data.get('appId')
    #     message = data.get('attributes').get('message')
    #     taskId = data.get('attributes').get('taskId')
    #     if message_type == "AnswerQuestion":
    #         _telegram_bot_answer_question(_get_user(user_id), message, _get_question(taskId))
    return HttpResponse()

# TODO The translation should happen here if needed before sending it to the user. During this 
# process the function should also save the translation where it is appropriate (corresponding 
# answer entry in answer_table).
def _telegram_bot_answer_question(user: User, message, question: Question):
    """
    Used to send the answer to the user. Functions is obsolete. Use send_answer_to_user instead.
    """
    try:
        bot = Bot(BOT_TOKEN)
        message = bot.send_message(user.telegram_id, f"You received an answer to the question \""
        f"{question.content[user.language]}\". The answer is: {message}")
    except Exception as e:
        logger.info('_telegram_bot_answer_question couldnt send answer')


def _get_user(user_id):
    """
    Helper function to find the `User` given their WeNet ID.
    """

    try:
        user: User = User.objects.get(id=user_id)
        return user
    except Exception as e:
        logger.info('_get_user - cannot get user using their wenet id'+str(user_id))

def _get_question(question_id):
    """
    Helper function to find the `Question` given its task ID.
    """
    try:
        question: Question = Question.objects.get(id=question_id)
        return question
    except Exception as e:
        logger.info('_get_question - cannot get user using their question id' + str(question_id))

@csrf_exempt
def get_best_answer(request: HttpRequest):
    """
    Helper function to find the `Best Answer` given its question ID.
    """
    try:
        if request.method == 'POST':
            try:
                question_id = request.POST.get('question_id')
            except:
                return HttpResponseBadRequest()
            if question_id:

                try:
                    question: Question = Question.objects.get(id=question_id)
                    best_answer_exists: Best_Answer = Best_Answer.objects.get(question=question)
                except:
                    best_answer_exists=None
            if best_answer_exists:
                logger.info("found answer")
                return JsonResponse({'best_answer':best_answer_exists.answer.content.__str__()})
            else:
                return JsonResponse({'best_answer': ''})
        return HttpResponse()
    except Exception as e:
        logger.exception('_get_question - cannot get user using their question id' + str(question_id))
        return HttpResponseBadRequest()

def _check_oauth2_tokens(dict: dict):
    """
    Helper function which checks if the OAuth 2.0 tokens where created correctly or not.
    """
    try:
        if (dict.keys().__contains__('error')):
            return HttpResponseBadRequest()
        return None
    except Exception as e:
        logger.info('_check_oauth2_tokens failed')

def _question_checks(user: User, question_id_field):
    """
    Helper function which checks whether a `Question` exists or not.
    """
    try:
        question: Question = Question.objects.get(id=question_id_field)
    except Question.DoesNotExist:
        return HttpResponseNotFound()

    try:
        if (question.user == user):
            return question
        else:
            return HttpResponseNotAllowed()
    except Exception as e:
        logger.info('_question_checks cannot send question to user')


def _update_user_token(user: User):
    """
    Used to create a new access and refresh token pair for the `User` to keep using the app.
    """
    try:
        oauth2_request = requests.post(WENET_TOKEN_GENERATOR, data={
            'grant_type' : 'refresh_token',
            'client_id' : APP_ID,
            'client_secret' : APP_SECRET,
            'refresh_token' : user.refresh_token
        }).json()

        user.access_token = oauth2_request['access_token']
        user.refresh_token = oauth2_request['refresh_token']
        user.save()
    except Exception as e:
        logger.info('_update_user_token cannot update user token to keep them signed in'+str(user.id))

def _translate(user: User, message: Question or Answer):
    try:
        translator = Translator()

        thread = Thread(target=_translate_to_english, args=(user, message))
        thread.start()
        thread.join()

        if (user.language == 'el'):
            message.content['tr'] = translator.translate(message.content['en'], dest='tr').text
        else:
            message.content['el'] = translator.translate(message.content['en'], dest='el').text

        message.save()
        if (isinstance(message, Answer)):
            _send_answer_to_user(message)
    except Exception as e:
        logger.info('_translate translation failed')

def _translate_to_english(user: User, message: Question or Answer):
    """
    Translates the given `Question` or `Answer` to English.
    """
    try:
        translator = Translator()

        message.content['en'] = translator.translate(message.content[user.language], src=user.language).text

        message.save()
    except Exception as e:
        logger.info('_translate_to_english  failed')


# Create your views here.

def index(request: HttpRequest):
    return HttpResponse("WeNet webhooks")

def authorise_user(request: HttpRequest):
    """
    Redirects the `User` to their telegram application so that they can connect they WeNet account
    with their Telegram account.
    """
    try:
        return redirect(f"{TELEGRAM_URI}{request.GET['code']}")
    except Exception as e:
        logger.info('authorise_user  failed to redirect user to telegram after wenet login')


@csrf_exempt
def create_account(request: HttpRequest):
    """
    Creates an account to the database using the `User`'s information.
    """
    try:
        oauth2_request = requests.post(WENET_TOKEN_GENERATOR, data={
            'grant_type': 'authorization_code',
            'client_id' : APP_ID,
            'client_secret' : APP_SECRET,
            'code' : request.POST['code']
        },timeout=1)
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
        user_profile_id = requests.get(f'{WENET_SERVICES}/token', headers=HEADERS, timeout=1).json()['profileId']
        user_details_request = requests.get(f'{WENET_SERVICES}/user/profile/{user_profile_id}', headers=HEADERS, timeout=1)
        user_details = user_details_request.json()
        user_name = user_details['name']
        language=user_details['locale']
        if language not in ('el', 'tr'):
            language = 'en'
        u = User(id = user_details['id'], telegram_id=request.POST['user_id'],
            name= f"{user_name['first']} {user_name['last']}", language=language,
            access_token=user_access_token, refresh_token=user_refresh_token)
        u.save()

        return JsonResponse({'message' : 'user_created', 'language': u.language})
    except Exception as e:
        logger.exception('create_account failed')

@csrf_exempt
def delete_account(request: HttpRequest):
    """
    Allows the `User` to delete their account.
    """
    try:
        try:
            user: User = User.objects.get(telegram_id=request.POST['user_id'])
        except User.DoesNotExist:
            return HttpResponseForbidden()

        user.delete()
        return HttpResponse()
    except:
        logger.info('delete_account failed')

# TODO Create a callback style funcction which will send the question to the appropriate users.

@csrf_exempt
def ask_question(request: HttpRequest):
    """
    Takes the `Question` that a `User` has posted, sends it to the WeNet application which will make
    the diverse `User` decision and translates the `Question` to the language of the other community.

    E.g.: If the `Question` was in Greek, it will get translated in Turkish.
    """
    try:
        user_id = request.POST['user_id']
        message = request.POST['question']
        try:
            user: User = User.objects.get(telegram_id=user_id)
        except User.DoesNotExist:
            return HttpResponseForbidden()

        question = Question(user=user, content={user.language : message})
        task_id = _create_wenet_question(question)
        if task_id:
            question.task_id = task_id
            question.save()
            thread = Thread(target=_translate, args=(user, question))
            thread.start()
        return HttpResponse()
    except Exception as e:
        logger.info('ask_question failed')

def _create_wenet_question(question: Question):
    """
    Helper function which creates a WeNet `Task` (`Question`).
    """
    try:
        HEADERS = {
            'Authorization' : question.user.access_token,
            'Accept' : APPLICATION_JSON
        }
        DATA = {
            'appId' : APP_ID,
            'requesterId' : str(question.user.id),
            'goal' : {
                'name' : question.content[question.user.language]
            },
            'taskTypeId' : TASK_TYPE_ID
        }

        request = requests.post(f'{WENET_SERVICES}/task', headers=HEADERS, json=DATA)

        if (request.status_code != 201):
            _update_user_token(question.user)
            HEADERS['Authorization'] = question.user.access_token
            request = requests.post(f'{WENET_SERVICES}/task', headers=HEADERS, json=DATA)

        return request.json().get('id')
    except Exception as e:
        logger.info('_create_wenet_question failed')

def _change_punctuations_to_raw(s: str):
    """
    Changes the given string to be suitable for the Telegram's Markdown V2.
    """
    new_string = ""
    for char in s:
        if (char in string.punctuation):
            new_string += f"\{char}"
        else:
            new_string += char
    return new_string

SEND_ANSWER_MESSAGE = {
    'en' : lambda a: r"*Your receive an answer to the question\:* "
        rf"_{_change_punctuations_to_raw(a.question.content['en'])}_\.""\n"
        rf"*The answer is\:* _{_change_punctuations_to_raw(a.content['en'])}_",
    'el' : lambda a: r"*Έχετε λάβει απάντηση στην ερώτηση\:* "
        rf"_{_change_punctuations_to_raw(a.question.content['el'])}_\.""\n"
        rf"*Η απάντηση είναι\:* _{_change_punctuations_to_raw(a.content['el'])}_",
    'tr' : lambda a: rf"_{_change_punctuations_to_raw(a.question.content['tr'])}_\, "
        r"*sorusuna cevap aldınız*\.""\n"r"*Aldığınız cevap\:*"
        rf"_{_change_punctuations_to_raw(a.content['tr'])}_"
}

def _send_answer_to_user(answer: Answer):
    """
    Sends the given `Answer` by a `User` to the questioner.
    """
    ANSWER_SOLVED_QUESTION = {
        'en': "Your questions are popular ! ",
        'el': "ευχαριστούμε για τη βοήθεια ✌",
        'tr': "Yardımlarınız için teşekkür ederim ✌"}
    MARK_BEST = {
        'en': "👍 Mark as best answer",
        'el': "👍 Καλύτερη απάντηση μέχρι τώρα",
        'tr': "👍 en iyi cevap olarak işaretle"}
    MARK_REPORT = {
        'en': "👎 Report answer",
        'el': "👎 Αναφορά ερώτησης",
        'tr': "👎Cevabı bildir"}
    IMPROVE_TRANSLATION = {
        'en': "🤝 improve translation",
        'el': "🤝 Βελτίωση μετάφρασης",
        'tr': "🤝 çeviriyi iyileştir"}

    try:
        bot = Bot(BOT_TOKEN)
        questioner: User = answer.question.user

        buttons = [[InlineKeyboardButton(MARK_BEST[questioner.language],callback_data={
                        'like_type' : 'like',
                        'question_id' : answer.question.id,
                        'answer_id' : answer.id
        }.__str__())], [InlineKeyboardButton(MARK_REPORT[questioner.language],callback_data={
                        'like_type' : 'dislike',
                        'answer_id' : answer.id
        }.__str__())], [InlineKeyboardButton(IMPROVE_TRANSLATION[questioner.language],callback_data={
                        'feedback_type' : 'improve_translation',
                        'answer_id' : answer.id
        }.__str__())]]
        logger.info({
                        'button_id' : 'dislike',
                        'question_id' : '20'
                    }.__str__())
        bot.send_message(questioner.telegram_id, SEND_ANSWER_MESSAGE[questioner.language](answer),reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN_V2)
        #bot.send_message(1595070759,reply_markup=InlineKeyboardMarkup(buttons), text="is your answer solved ?")
    except Exception as e:
        logger.info('_send_answer_to_user failed')

@csrf_exempt
def set_best_answer(request: HttpRequest):
    try:
        THANKS_FOR_FEEDBACK = {
            'en': "thank your for your help ✌",
            'el': "ευχαριστούμε για τη βοήθεια ✌",
            'tr': "Yardımlarınız için teşekkür ederim ✌"}
        if request.method == 'POST':
            question_id = request.POST.get('question_id')
            answer_id = request.POST.get('answer_id')
            user_id = request.POST.get('user_id')
            question: Question = Question.objects.get(id=question_id)
            answer: Answer = Answer.objects.get(id=answer_id)
            answerer: User = User.objects.get(telegram_id=user_id)
            try:
                best_answer_exists: Best_Answer = Best_Answer.objects.get(question=question)
            except:
                best_answer_exists=None
            if best_answer_exists:
                best_answer_exists.answer = answer
                best_answer_exists.save()
                bot = Bot(BOT_TOKEN)
                bot.send_message(user_id, text=THANKS_FOR_FEEDBACK[answerer.language],
                                 parse_mode=ParseMode.MARKDOWN_V2)
            else:
                best_answer = Best_Answer(question=question, answer=answer)
                best_answer.save()
                question.solved = True
                question.save()
                bot = Bot(BOT_TOKEN)
                bot.send_message(user_id, text=THANKS_FOR_FEEDBACK[answerer.language],
                                 parse_mode=ParseMode.MARKDOWN_V2)
            return HttpResponse()
    except Exception as e:
        logger.exception('_send_answer failed')
        return HttpResponseBadRequest()

@csrf_exempt
def set_answer_feedback(request: HttpRequest):
    try:
        THANKS_FOR_FEEDBACK = {
            'en': "thank your for your help ✌",
            'el': "ευχαριστούμε για τη βοήθεια ✌",
            'tr': "Yardımlarınız için teşekkür ederim ✌"}
        SOMETHING_WRONG = {
            'en': "Feedback not saved ☹ something went wrong",
            'el': "Κάτι πήγε λάθος , το σχόλιο δεν αποθηκεύτηκε ☹ ",
            'tr': "Geri bildirim kaydedilmedi ☹ bir şeyler ters gitti"}
        if request.method == 'POST':

            user_id = request.POST.get('user_id')
            answer_id = request.POST.get('answer_id')
            message = request.POST.get('message')
            answerer: User = User.objects.get(telegram_id=user_id)
            answer: Answer = Answer.objects.get(id=answer_id)
            if answer and answerer and message:
                answer_feedback = Answer_Feedback(answer=answer, user=answerer, content={answerer.language: message})
                answer_feedback.save()
                bot = Bot(BOT_TOKEN)
                bot.send_message(user_id, text=THANKS_FOR_FEEDBACK[answerer.language],
                                 parse_mode=ParseMode.MARKDOWN_V2)

            else:
                bot = Bot(BOT_TOKEN)
                bot.send_message(user_id, text=SOMETHING_WRONG[answerer.language],
                                 parse_mode=ParseMode.MARKDOWN_V2)
            return HttpResponse()
    except Exception as e:
        logger.exception('_send_answer failed')
        return HttpResponseBadRequest()

@csrf_exempt
def notify_admin(request: HttpRequest):
    try:
        THANKS_FOR_FEEDBACK = {
            'en': "thank your for your help ✌",
            'el': "ευχαριστούμε για τη βοήθεια ✌",
            'tr': "Yardımlarınız için teşekkür ederim ✌"}
        if request.method == 'POST':
            try:
                answer_id = request.POST.get('answer_id')
                user_id = request.POST.get('user_id')
                answerer: User = User.objects.get(telegram_id=user_id)
            except:
                return HttpResponseBadRequest("problem with answer id or user id")

            try:
                if answer_id and answerer:
                    bot = Bot(BOT_TOKEN)
                    bot.send_message(1595070759, text="**Reported question**" + str(answer_id),parse_mode=ParseMode.MARKDOWN_V2)
                    bot.send_message(answerer.telegram_id, text=THANKS_FOR_FEEDBACK[answerer.language],
                                     parse_mode=ParseMode.MARKDOWN_V2)
            except:
                return HttpResponseBadRequest("problem with bot msg")

            return HttpResponse()
    except Exception as e:
        logger.info('_send_answer failed')
        return HttpResponseBadRequest()

@csrf_exempt
def send_answer(request: HttpRequest):
    """
    Takes the `Answer` a `User` has posted for translation and saves is under the correct `Question`.
    """
    try:
        try:
            user_id = request.POST['user_id']
            question_id = request.POST['question_id']
            message = request.POST['answer']
        except:
            logger.exception("Could not get data from POST request")
            return HttpResponseBadRequest()
        if user_id and question_id and message:
            answerer: User = User.objects.get(telegram_id=user_id)
            question: Question = Question.objects.get(id=question_id)
            questioner: User = question.user

            if (_create_wenet_answer(message, answerer, question)):
                answer = Answer(user=answerer, question=question, content={answerer.language : message})
                answer.save()

                if (answerer.language == questioner.language):
                    _send_answer_to_user(answer)
                else:
                    thread = Thread(target=_translate, args=(answerer, answer))
                    thread.start()
                    thread.join()

                return HttpResponse()
            return HttpResponseBadRequest()
    except Exception as e:
        logger.info('_send_answer failed')
        return HttpResponseBadRequest()

def _create_wenet_answer(answer: str, answerer: User, question: Question):
    """
    Helper function which creates a WeNet `Transcation` (`Answer`) on the given `Task` (`Question`).
    """
    try:
        HEADERS = {
            'Authorization' : answerer.access_token,
            'Accept' : APPLICATION_JSON
        }
        DATA = {
            'taskId' : question.task_id,
            'label' : 'AnswerQuestion',
            'attributes' : {
                'message' : answer
            },
            'actioneerId' : str(answerer.id),
            '_creationTs' : int(time.time()*1000.0),
            '_lastUpdateTs' : int(time.time()*1000.0),

        }
        response = requests.post(f'{WENET_SERVICES}/task/transaction', headers=HEADERS, json=DATA)

        if (response.status_code != 201):
            _update_user_token(answerer)
            HEADERS['Authorization'] = answerer.access_token
            response = requests.post(f'{WENET_SERVICES}/task', headers=HEADERS, json=DATA)
        return response.ok
    except Exception as e:
        logger.info('_create_wenet_answer failed')


def asked_questions(request: HttpRequest):
    """
    Returns to the requesting `User` the `Questions` that they have asked.
    """
    try:
        user_id = request.GET['user_id']
        try:
            user: User = User.objects.get(telegram_id=user_id)
        except User.DoesNotExist:
            return HttpResponseForbidden()

        questions = Question.objects.filter(user=user, solved=False)

        result = []

        for question in questions:
            result.append({
                'id' : question.id,
                'text' : question.content[user.language]
            })

        return JsonResponse({'questions' : result})
    except Exception as e:
        logger.info('asked_questions failed')

@csrf_exempt
def mark_as_solved(request: HttpRequest):
    """
    Allows a `User` to mark one of their `Questions` as solved.
    """
    try:
        user: User = User.objects.get(telegram_id=request.POST['user_id'])
        result = _question_checks(user, request.POST['question_id'])

        if (isinstance(result, Question)):
            result.solved = True
            result.save()
            return HttpResponse()
        else:
            return result
    except Exception as e:
        logger.info('mark_as_solved failed')

@csrf_exempt
def mark_as_unsolved(request: HttpRequest):
    """
    Allows a `User` to mark one of their `Questions` as unsolved.
    """
    try:
        result: Question = Question.objects.get(id=request.POST['question_id'])

        result.solved = False
        result.save()

        return HttpResponse()

    except Exception as e:
        logger.info('mark_as_un_solved failed')

def question_answers(request: HttpRequest):
    """
    Returns to a `User` the `Answers` that they have received for the selected `Question`.
    """
    try:
        user: User = User.objects.get(telegram_id=request.GET['user_id'])
        result = _question_checks(user, request.GET['question_id'])

        if (isinstance(result, Question)):
            answers = result.answer_set.all()
            result = []
            for answer in answers:
                result.append({
                    'id' : answer.id,
                    'text' : answer.content[user.language]
                })
            return JsonResponse({'answers' : result})
        else:
            return result
    except Exception as e:
        logger.exception('question_answers failed')

# FIXME This function should call the WeNet server and find the appopriate questions that the current
# user should see.
def available_questions(request: HttpRequest):
    """
    Returns to a `User` all the available `Questions` that they can answer. These `Questions` 
    will have been already selected by the WeNet's diversity algorithm.
    """
    try:
        try:
            user: User = User.objects.get(telegram_id=request.GET['user_id'])
        except User.DoesNotExist:
            return HttpResponseForbidden()

        result = []
        for question in Question.objects.filter(solved=False).exclude(user=user):
            result.append({
                'id' : question.id,
                'content' : question.content[user.language]
            })
        random_items = random.sample(result, 10)
        return JsonResponse({'questions' : random_items})
    except Exception as e:
        logger.exception('mark_as_solved failed')
        return HttpResponseBadRequest()

@csrf_exempt
def delete_question(request: HttpRequest):
    """
    Allows a `User` to delete their selected posted `Question`.
    """
    try:
        user: User = User.objects.get(telegram_id=request.POST['user_id'])
        question: Question = Question.objects.get(id=request.POST['question_id'])
        query_result = question.delete()

        if (query_result[0] > 0):
            return HttpResponse()

        return HttpResponseBadRequest()
    except Exception as e:
        logger.info('delete_question failed')

def solved_questions(request: HttpRequest):
    """
    Returns to a `User` all of their solved `Questions`. These `Questions` would have been marked a 
    solved by the `User`.
    """
    try:
        try:
            user: User = User.objects.get(telegram_id=request.GET['user_id'])
        except User.DoesNotExist:
            return HttpResponseForbidden()

        questions = Question.objects.filter(user=user, solved=True)

        result = []

        for question in questions:
            result.append({
                'id' : question.id,
                'text' : question.content[user.language]
            })

        return JsonResponse({'questions' : result})
    except Exception as e:
        logger.info('solved_question failed')