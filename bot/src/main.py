import logging
import requests
import webbrowser

from telegram import BotCommand, Message, Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

APP_ID = 'mH7Tbcd0W5'

TESTING_SERVER = 'https://localhost/wenet'
SOCIALAB_SERVER = 'https://cognition-srv2.ouc.ac.cy/wenet'
SERVER = TESTING_SERVER
WENET_WEBSITE = 'https://wenet.u-hopper.com/dev/hub/frontend'
WENET_AUTHENTICATION = f'https://wenet.u-hopper.com/dev/hub/frontend/oauth/login?client_id={APP_ID}'

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
        update.message.reply_text(f"Hi {user.first_name}!")
    else:
        # This part creates a new user in the database which connect their accounts (Telegram, WeNet)
        request = requests.post(f'{SERVER}/create_user', params={
            'code' : passed_arguments[0],
            'user_id' : user.id,
        }, verify=False)
        # TODO Handle both the 'user_created' and 'code_error' to give user feedback.
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

def askquestion(update: Update, context: CallbackContext):
    """
    It can be used by the user to make a question, which will be send to the appropriate users 
    according to the WeNet platform.
    """
    message = update.message
    if (message != None):
        # TODO The following two lines will have to be removed and replaced with the code bellow,
        # or new code
        # message.reply_text("Not implemented yet.")
        # return
        user = update.effective_user
        passed_arguments = context.args
        PASSED_ARGUMENTS_LENGTH = len(passed_arguments)
        # print(PASSED_ARGUMENTS_LENGTH, passed_arguments)
        # arguments = message.text.replace('/askquestion', '')
        # FIRST_QUOTATION_MARK = arguments.find('"')
        # LAST_QUOTATION_MARK = arguments.find('"', 2)
        # print(arguments, FIRST_QUOTATION_MARK,LAST_QUOTATION_MARK)
        # for argument in arguments:
        #     print(passed_arguments[0])
        #     passed_arguments.remove(argument)
        # print(passed_arguments)

        if (PASSED_ARGUMENTS_LENGTH == 0):
            message.reply_text("Remember, you need to write the question you are looking for an "
            "answer!")
        # elif (PASSED_ARGUMENTS_LENGTH > 1):
        #     message.reply_text("Too many arguments.")
        else:
            # message.reply_text(f"Your question: {' '.join(passed_arguments)}")
            request = requests.post(f'{SERVER}/ask_question', data={
                'user_id' : user.id,
                'question' : ' '.join(passed_arguments),
            }, verify=False)

            if (request.status_code == 200):
                message.reply_text("Question was submitted successfully!")

def available_questions(update: Update, context: CallbackContext):
    """
    Texts the user with the available (unanswered) questions that they have according to the WeNet 
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
    # else:
    #     message = update.edited_message

        # TODO The following two lines will have to be removed and replaced with the code bellow,
        # or new code
        # message.reply_text("Not implemented yet.")
        # return

        user = update.effective_user
        passed_arguments = context.args
        PASSED_ARGUMENTS_LENGTH = len(passed_arguments)
        
        if (PASSED_ARGUMENTS_LENGTH == 0):
            # message.reply_text(f"You need to give the number of the question you would like to answer!")
            message.reply_text("You need to give the question id followed by the answer.")
        # elif (PASSED_ARGUMENTS_LENGTH > 2):
        #     message.reply_text(f"You gave me more that two arguments!")
        elif (not passed_arguments[0].isdigit()):
            message.reply_text("You need to give the number of the question first.")
            # message.reply_text(f"I can only understand numbers!")
        else:
            request = requests.post(f'{SERVER}/send_answer', data={
                'user_id' : user.id,
                'question_id' : passed_arguments[0],
                'answer' : ' '.join(passed_arguments[1:]),
            }, verify=False)

            if (request.status_code == 200):
                message.reply_text("Answer was submitted successfully!")
            # passed_argument = int(passed_arguments[0])
            # message.reply_text(f"Argument passed: {passed_argument}")


def asked_questions(update: Update, context: CallbackContext):
    """
    It can be used by a user to see their asked questions.
    """
    message = update.message
    if (message is not None):
        # TODO The following line shoule be removed and replaced with the implementation
        message.reply_text("Not implemented yet.")

def question_answers(update: Update, context: CallbackContext):
    """
    It can be used by the user to see all the answers that their selected question received.
    """
    message = update.message
    if (message is not None):
        # TODO The following line shoule be removed and replaced with the implementation
        message.reply_text("Not implemented yet.")

def mark_as_solved(update: Update, context: CallbackContext):
    """
    It should be used by a user to mark when a question has been solved.
    """
    message = update.message
    if (message is not None):
        # TODO The following line shoule be removed and replaced with the implementation
        message.reply_text("Not implemented yet.")
        
def create_account(update: Update, context: CallbackContext):
    message = update.message
    if (message is not None):
        # TODO Show the user a link where the can create a profile
        message.reply_text("Not implemented yet.")

def login(update: Update, context: CallbackContext):
    message = update.message
    if (message is not None):
        webbrowser.open('https://wenet.u-hopper.com/dev/hub/frontend/oauth/login?client_id=mH7Tbcd0W5')

def main() -> None:
    bot = Bot('5190722737:AAHrk9MCT01h646wPP9G5M2qjOYm3fiRYtw')
    bot.set_my_commands(commands=[
        BotCommand('help', HELP_INFORMATION),
        BotCommand('login', LOGIN_INFORMATION),
        BotCommand('askquestion', ASK_QUESTION_INFORMATION),
        BotCommand('availablequestions', AVAILABLE_QUESTIONS_INFORMATION),
        BotCommand('answer', ANSWER_INFORMATION),
        BotCommand('askedquestions', ASKED_QUESTIONS_INFORMATION),
        BotCommand('questionanswers', QUESTION_ANSWERS_INFORMATION),
        BotCommand('markassolved', MARK_QUESTION_AS_SOLVED)])
    updater = Updater('5190722737:AAHrk9MCT01h646wPP9G5M2qjOYm3fiRYtw')
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('askquestion', askquestion))
    dispatcher.add_handler(CommandHandler('availablequestions',
    available_questions))
    dispatcher.add_handler(CommandHandler('answer', answer))
    dispatcher.add_handler(CommandHandler('askedquestions', asked_questions))
    dispatcher.add_handler(CommandHandler('questionanswers', question_answers))
    dispatcher.add_handler(CommandHandler('markassolved', mark_as_solved))
    dispatcher.add_handler(CommandHandler('login', login))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
