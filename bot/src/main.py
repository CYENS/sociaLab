import json
import logging
import string
import requests
import os

from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler

BOT_TOKEN = os.environ['BOT_TOKEN']

APP_ID = os.environ['APP_ID']
SERVER = os.environ['SERVER']
WENET_WEBSITE = os.environ['WENET_WEBSITE']
WENET_AUTHENTICATION = os.environ['WENET_AUTHENTICATION']

LOGIN_INFORMATION = "login to your WeNet account and establish a connection with your Telegram account"
ASK_QUESTION_INFORMATION = "ask the community a question"
AVAILABLE_QUESTIONS_INFORMATION = "show the available questions by the community to you"
ANSWER_INFORMATION = r"answer a question \- requires question number and then the answer"
ASKED_QUESTIONS_INFORMATION = "show all the questions that you asked"
QUESTION_ANSWERS_INFORMATION = r"get the answers of a question you made \- requires question number"
HELP_INFORMATION = "provides a help message"
MARK_QUESTION_AS_SOLVED = "marks the question as solved so other won't have to answer it"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    """
    Used when the user invites the bot to start chatting.
    """
    user = update.effective_user
    passed_arguments = context.args

    if (len(passed_arguments) == 0):
        update.message.reply_text(f"Hi {user.first_name}! Welcome to Socialab")
    else:
        # This part creates a new user in the database which connect their accounts (Telegram, WeNet)
        request = requests.post(f'{SERVER}/create_user', data={
            'code' : passed_arguments[0],
            'user_id' : user.id,
        }, verify=False)
        if (request.status_code == 400):
            update.message.reply_text('Could not establish a connection.\nPlease try again.')
        else:
            update.message.reply_text('Connection created!')
        update.message.delete()
        
def help(update: Update, context: CallbackContext):
    """
    Can be used by the user to print (text) them the available actions.
    """
    user = update.effective_user

    update.message.reply_markdown_v2(rf"Hi {user.first_name}\!""\nThese are the "
    r"available commands\:""\n"
    rf"/login \- {LOGIN_INFORMATION}""\n"
    # r"/start Used when a user logins in for the first time\.""\n"
    rf"/askquestion \- {ASK_QUESTION_INFORMATION} E\.g\.\:""\n"
    "\t\t"r" _/askquestion Are there any good restaurants in Kyreneia\?_""\n"
    rf"/availablequestions \- {AVAILABLE_QUESTIONS_INFORMATION}""\n"
    rf"/answer \- {ANSWER_INFORMATION} E\.g\.\:""\n"
    "\t\t"r"_/answer 4578 Yes\, there is one by the port\!_""\n"
    rf"/askedquestions \- {ASKED_QUESTIONS_INFORMATION}""\n"
    rf"/questionanswers \- {QUESTION_ANSWERS_INFORMATION} E\.g\.\:""\n"
    "\t\t"r"_/questionanwers 4578_""\n"
    rf"/markassolved \- {MARK_QUESTION_AS_SOLVED} E\.g\.\:""\n"
    "\t\t"r"_/markassolved 4578_""\n"
    rf"/help \- {HELP_INFORMATION}""\n")

def ask_question(update: Update, context: CallbackContext):    
    """
    It can be used by the user to make a question, which will be send to the appropriate users 
    according to the WeNet platform.
    """

    update.message.reply_text("Type the question that you want to ask")
    return 0

def ask_question_handler(update: Update, context: CallbackContext):
    message = update.message
    user = update.effective_user

    if (message is not None):
        request = requests.post(f'{SERVER}/ask_question', data={
                'user_id' : user.id,
                'question' : message.text,
            }, verify=False)

        if (request.status_code == 200):
            message.reply_text("Question was submitted successfully!")
        else:
            message.reply_text("Question could not be sumbitted. Please try again.")
    # message.reply_text(f"You asked: \"{message.text}\".")
    return ConversationHandler.END

def available_questions(update: Update, context: CallbackContext):
    """
    Texts the user with the available (unsolved) questions that they have according to the WeNet 
    platform.
    """
    message = update.message
    if (message != None):
        # TODO The following line shoule be removed and replaced with the implementation
        message.reply_text("Not implemented yet.")

def answer(update: Update, context: CallbackContext):
    """
    It can be used by a user to answer a question that they are given.
    """
    message = update.message
    if (message is not None):

        user = update.effective_user
        passed_arguments = context.args
        PASSED_ARGUMENTS_LENGTH = len(passed_arguments)
        
        if (PASSED_ARGUMENTS_LENGTH == 0):
            message.reply_text("You need to give the question id followed by the answer.")
        elif (not passed_arguments[0].isdigit()):
            message.reply_text("You need to give the number of the question first.")
        else:
            request = requests.post(f'{SERVER}/send_answer', data={
                'user_id' : user.id,
                'question_id' : passed_arguments[0],
                'answer' : ' '.join(passed_arguments[1:]),
            }, verify=False)

            if (request.status_code == 200):
                message.reply_text("Answer was submitted successfully!")

def asked_questions(update: Update, context: CallbackContext):
    """
    It can be used by a user to see their asked questions.
    """
    message = update.message
    if (message is not None):
        user = update.effective_user
        request = requests.get(f'{SERVER}/asked_questions', params={
            'user_id' : user.id
        }, verify=False)
        questions: list = request.json()['questions']
        result = "ID - Question\n"
        
        markup_list = []
        
        for question in questions:
            markup_list.append([InlineKeyboardButton(question['text'], callback_data={
                "id" : question['id'],
                "type" : 'answers'
            }.__str__())])
            result += f"{question['id']} - {question['text']}\n"
        
        message.reply_markdown_v2(r"_*__These are all the questions that you have asked__\:*""\n"
            r"\(by pressing a question, you can see it's answers\)_""\n",
            reply_markup=InlineKeyboardMarkup(markup_list))
        return 0

def selected_question_choice(update: Update, context: CallbackContext):
    """
    Depending on the question that the user (submitter) selected, it shows the possible actions:
        - to see the answers
        - to mark the question as solved
        - or nothing 
    """
    query = update.callback_query
    data = json.loads(query.data.replace("'",'"'))
    message = query.message
    user = query.from_user
    chat = update.effective_chat

    if (message is not None):
        if (data['type'] == 'answers'):
            markup_list = [
                [KeyboardButton("See answers")],
                [KeyboardButton("Mark as solved")],
                [KeyboardButton("Cancel")]
            ]            
            
            context.user_data['question'] = data
            message.reply_text(text= "What you would you like to know about that question?",
                reply_markup=ReplyKeyboardMarkup(markup_list, one_time_keyboard=True))
    return 1

def question_manipulation(update: Update, context: CallbackContext):
    """
    This does handles the action that the user has selected from `selected_question_choice`. It either
    finds the answers or marks the question as solved.
    """
    DATA = context.user_data['question']
    MESSAGE = update.message
    MESSAGE_CONTENT = MESSAGE.text.lower()
    USER = update.effective_user

    if (MESSAGE is not None):
        if ('see answers' in MESSAGE_CONTENT) :
            request = requests.get(f'{SERVER}/question_answers', params={
                    'user_id' : USER.id,
                    'question_id' : DATA['id']
                }, verify=False)
                
            answers: list = request.json()['answers']
            result = ""

            for answer in answers:
                result += f"{answer['id']} - {answer['text']}\n"
            
            new_result = ""
            for character in result:
                if (character in string.punctuation):
                    new_result += f"\{character}"
                else:
                    new_result += character
            if (new_result == ""):
                MESSAGE.reply_text("No one answered yet.")
            else:
                MESSAGE.reply_markdown_v2(f'_{new_result}_')
        elif ('mark as solved' in MESSAGE_CONTENT):
            request = requests.post(f'{SERVER}/mark_as_solved', data={
                'user_id' : USER.id,
                'question_id' : DATA['id']
            }, verify=False)
            
            if (request.status_code == 200):
                MESSAGE.reply_text(f"The question was successfully marked a solved!")
            else:
                MESSAGE.reply_text("Error")
        else:
            MESSAGE.reply_text("I'm sorry I couldn't understand what you typed.")
    return ConversationHandler.END
        
def login(update: Update, context: CallbackContext):
    message = update.message
    if (message is not None):
        update.message.reply_html(
            f'<a href="http://wenet.u-hopper.com/dev/hub/frontend/oauth/login?client_id={APP_ID}">Login to Wenet</a>')
        #webbrowser.open(f'https://wenet.u-hopper.com/dev/hub/frontend/oauth/login?client_id={APP_ID}')

def stop(update: Update, context: CallbackContext):
    update.message.reply_text("Process stopped.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def nothing(update: Update, context: CallbackContext):
    return ConversationHandler.END

def main() -> None:
    bot = Bot(BOT_TOKEN)
    bot.set_my_commands(commands=[
        BotCommand('help', HELP_INFORMATION),
        BotCommand('login', LOGIN_INFORMATION),
        BotCommand('ask_question', ASK_QUESTION_INFORMATION),
        BotCommand('availablequestions', AVAILABLE_QUESTIONS_INFORMATION),
        BotCommand('answer', ANSWER_INFORMATION),
        BotCommand('asked_questions', ASKED_QUESTIONS_INFORMATION),
        BotCommand('questionanswers', QUESTION_ANSWERS_INFORMATION),
        BotCommand('markassolved', MARK_QUESTION_AS_SOLVED)])
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    stop_handlers = [
        CommandHandler('stop', stop),
        MessageHandler(Filters.regex('^[C|c]ancel.?$') | Filters.regex('^[D|d]one.?$'), stop),
    ]

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))
    # dispatcher.add_handler(CommandHandler('askquestion', askquestion))
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('ask_question', ask_question)],
        states={
            0 : [MessageHandler(
                Filters.text &  ~(Filters.command | Filters.regex('^[D|d]one[.|$]')),
                ask_question_handler
            )]
        },
        fallbacks=stop_handlers,
    ))
    
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('asked_questions', asked_questions)],
        states={
            0 : [CallbackQueryHandler(selected_question_choice)],
            1 : [MessageHandler(
                Filters.text & ~(Filters.regex('^[C|c]ancel.?$') | Filters.regex('^[D|d]one.?$') | 
                Filters.command), question_manipulation)]
        },
        fallbacks=stop_handlers,
    ))
    
    dispatcher.add_handler(CommandHandler('availablequestions',
    available_questions))
    dispatcher.add_handler(CommandHandler('answer', answer))
    dispatcher.add_handler(CommandHandler('login', login))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
