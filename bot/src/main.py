import json
import logging
import string
import requests
import os

from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler, PicklePersistence

# BOT_TOKEN = os.environ['BOT_TOKEN']

# APP_ID = os.environ['APP_ID']
# SERVER = os.environ['SERVER']
# WENET_WEBSITE = os.environ['WENET_WEBSITE']
# WENET_AUTHENTICATION = os.environ['WENET_AUTHENTICATION']
BOT_TOKEN = '5397987170:AAGEspN33gK8ZReJgCwRZ1nHwKVeF4KGgYY'
APP_ID = 'mH7Tbcd0W5'
SERVER = 'http://localhost/wenet'

LOGIN_INFORMATION = {
    'en' : "login to your WeNet account and establish a connection with your Telegram account",
    'gr' : "συνδεθήτε στο λογαριασμό σας στο WeNet για να δημιουργήσετε μια σύνδεση με το λογαριασμό σας στο Telegram",
    'tr' : "WeNet hesabınıza giriş yapın ve Telegram hesabınızla bağlantı kurun"
}
ASK_QUESTION_INFORMATION = {
    'en' : "ask the community a question",
    'gr' : "κάντε μια ερώτηση στην κοινότητά μας",
    'tr' : "Gruba soru sorun"
}
AVAILABLE_QUESTIONS_INFORMATION = {
    'en' : "shows the available questions for you to answer",
    'gr' : "σας δείχνει τις διαθέσιμες ερωτήσεις που έχετε",
    'tr' : "Size cevaplayabileceğiniz mevcut soruları gösterir"
}
ASKED_QUESTIONS_INFORMATION = {
    'en' : "shows all the questions that you asked and allows you to manipulate them",
    'gr' : "σας δείχνει όλες τις ερωτήσεις που έχετε υποβάλει όπου μπορείτε να τις διαχειριστείτε",
    'tr' : "Size sormuş olduğunuz tüm soruları gösterir ve üzerlerinde değişiklik yapmanıza izin verir"
}
STOP_INFORMATION = {
    'en' : r"allows you to stop/interrupt a process that you have started\. A process is started "\
        r"by using /ask\_question, /available\_questions, /asked\_questions and processes in them",
    'gr' : r"σας επιτρέπει να σταματήσετε τη διαδικασία που έχετε αρχίσει με μια από τις "\
        r"εντολές\: /ask\_question, /available\_questions και /asked\_questions",
    'tr' : r"Başlatmış olduğunuz süreci durdurmak/kesintiye uğratmak için size izin verir. Süreç "\
        r"/ask\_question, /available\_questions, /asked\_questions komutlarını kullanarak başlar "\
        "ve devam ede"
}
HELP_INFORMATION = {
    'en' : "provides a help message",
    'gr' : "σας παρέχει βοήθημα",
    'tr' : "Yardım mesajı gösterir"
}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

CONNECTION_FAILED = {
    'en' : "Could not establish a connection.\nPlease try again.",
    'gr' : "Δεν μπορέσαμε σας συνδέσουμε. Παρακαλώ δοκιμάστε ξανά.",
    'tr' : "Bağlantı kurulamadı. Lütfen yeniden deneyiniz."
}
CONNECTION_SUCCEDED = {
    'en' : "Connection created!",
    'gr' : "Η σύνδεση έχει δημιουργηθεί!",
    'tr' : "Bağlantı kuruldu!"
}

def start(update: Update, context: CallbackContext):
    """
    Used when the user invites the bot to start chatting.
    """
    user = update.effective_user
    passed_arguments = context.args

    if (len(passed_arguments) == 0):
        context.chat_data['language'] = 'en'
        update.message.reply_markdown_v2(rf"*_Welcome to sociaLa\!_* The default language is"
        r"English\. For Greek send /gr and for Turkish /tr\.""\n"r"*_Καλως ορίσατε στο sociaLab\!_* "
        r"Η καθορισμένη γλώσσα είναι τα Αγγλικά\. Για Ελληνικά στείλτε /gr και για Τουρκικά /tr\.""\n"
        r"*_SociaLab’ a hoşgeldiniz\!_* Varsayılan dil İngilizce’dir\. Yunanca için /gr ve Türkçe için "
        r"/tr yazıp gönderiniz\.")
    else:
        # This part creates a new user in the database which connect their accounts (Telegram, WeNet)
        request = requests.post(f'{SERVER}/create_user', data={
            'code' : passed_arguments[0],
            'user_id' : user.id,
        }, verify=False)
        LANGUAGE = context.chat_data['language']
        if (request.status_code == 400):
            update.message.reply_text(CONNECTION_FAILED[LANGUAGE])
        else:
            update.message.reply_text(CONNECTION_SUCCEDED[LANGUAGE])
        update.message.delete()
        
def help(update: Update, context: CallbackContext):
    """
    Can be used by the user to print (text) them the available actions.
    """
    user = update.effective_user
    LANGUAGE = context.chat_data['language']
    update.message.reply_markdown_v2(rf"Hi _{user.first_name}_\!""\n"
    r"*These are the available commands*\:""\n"
    rf"• /login \- _{LOGIN_INFORMATION[LANGUAGE]}_""\n"
    rf"• /ask\_question \- _{ASK_QUESTION_INFORMATION[LANGUAGE]}_""\n"
    rf"• /available\_questions \- _{AVAILABLE_QUESTIONS_INFORMATION[LANGUAGE]}_""\n"
    rf"• /asked\_questions \- _{ASKED_QUESTIONS_INFORMATION[LANGUAGE]}_""\n"
    rf"• /stop \- _{STOP_INFORMATION[LANGUAGE]}_""\n"
    rf"• /help \- _{HELP_INFORMATION[LANGUAGE]}_""\n"
    r"• /en For English""\n"r"• /gr Για Ελληνικά""\n"r"• /tr Türkçe için")

ASK_QUESTION = {
    'en' : "Type your question.",
    'gr' : "Πληκτρολογήστε την ερώτηση που έχετε.",
    'tr' : "Sorunuzu yazınız."
}

def ask_question(update: Update, context: CallbackContext):    
    """
    It can be used by the user to make a question, which will be send to the appropriate users 
    according to the WeNet platform.
    """
    update.message.reply_text(ASK_QUESTION[context.chat_data['language']])
    return 0

QUESTION_SUCCEDED = {
    'en' : "Your question was submitted successfully!",
    'gr' : "Η ερώτηση σας καταχωρήθηκε επιτυχώς!",
    'tr' : "Sorunuz başarıyla gönderildi!"
}

QUESTION_FAILED = {
    'en' : "Your question could not be submitted. Please try again.",
    'gr' : "Η ερώτηση σας δεν μπόρεσε να καταχωρηθεί. Παρακαλώ δοκιμάστε ξανά.",
    'tr' : "Sorunuz gönderilemedi. Lütfen tekrar deneyiniz."
}

def ask_question_handler(update: Update, context: CallbackContext):
    """
    Handles the question typed by the user by sending it to the server.
    """
    message = update.message
    user = update.effective_user

    if (message is not None):
        request = requests.post(f'{SERVER}/ask_question', data={
                'user_id' : user.id,
                'question' : message.text,
            }, verify=False)

        if (request.status_code == 200):
            message.reply_text(QUESTION_SUCCEDED[context.chat_data['language']])
        else:
            message.reply_text(QUESTION_FAILED[context.chat_data['language']])
    return ConversationHandler.END

NO_AVAILABLE_QUESTIONS = {
    'en' : "Currently there are no questions for you.",
    'gr' : "Προς το παρόν δεν υπάρχουν ερωτήσεις για εσάς.",
    'tr' : "Şu an sizin için herhangi bir soru yok."
}

AVAILABLE_QUESTIONS = {
    'en' : r"_*__These are all the questions available for you to answer\:__*""\n"
        r"\(by pressing a question, you can answer it\)_""\n",
    'gr' : r"_*__Αυτές είναι όλες οι ερωτήσεις που έχετε στη διάθεση σας για να απαντήσετε\:__*""\n"
        r"\(πατώντας μια ερώτηση, μπορείτε να την απαντήσετε\)_""\n",
    'tr' : r"_*__Cevaplamanız için hazır olan tüm sorular bunlar\:__*""\n"
        r"\(soruların üzerine tıklayarak cevap verebilirsiniz\)_""\n"
}

def available_questions(update: Update, context: CallbackContext):
    """
    Texts the user with the available (unsolved) questions that they have according to the WeNet 
    platform.
    """
    message = update.message
    USER = update.effective_user

    if (message != None):
        request = requests.get(f'{SERVER}/available_questions', params= {'user_id' : USER.id}, verify=False)

        if (request.status_code == 200):
            markup_list = []
            questions: list = request.json()['questions']
            for (index, question) in enumerate(request.json()['questions']):
                markup_list.append(InlineKeyboardButton(question['content'], callback_data={
                    'button_id' : index,
                    'question_id' : question['id'],
                    'type' : 'available'
                }.__str__()))
            result = ""
            for (index, question) in enumerate(questions):
                result += f"{index + 1} - {question['content']}\n"
            
            if (result == ""):
                message.reply_text(NO_AVAILABLE_QUESTIONS[context.chat_data['language']])
            else:
                message.reply_markdown_v2(AVAILABLE_QUESTIONS[context.chat_data['language']],
                    reply_markup=InlineKeyboardMarkup.from_column(markup_list))
        return 0

TYPE_ANSWER = {
    'en' : "Please type your answer:",
    'gr' : "Παρακαλώ πληκτρολογήστε την απάντηση σας:",
    'tr' : "Lütfen cevabınızı yazınız:"
}

NO_SUCH_ANSWER = {
    'en' : "I'm sorry, I couldn't understand what you typed.",
    'gr' : "Λυπάμαι, δεν μπόρεσα να καταλάβω τι πληκτρολογήσατε.",
    'tr' : "Üzgünüm, ne yazdığınızı anlayamadım."
}

def available_question_manipulation(update: Update, context: CallbackContext):
    """
    Handles the response of the user given their choice from the questions listed.
    """
    MESSAGE = update.message
    MESSAGE_CONTENT = MESSAGE.text.lower()
    LANGUAGE = context.chat_data['language']

    if (MESSAGE is not None):
        if (YES[LANGUAGE].lower() in MESSAGE_CONTENT):
            MESSAGE.reply_text(TYPE_ANSWER[LANGUAGE],
                reply_markup=ReplyKeyboardRemove())
            return 1
        else:
            MESSAGE.reply_text(NO_SUCH_ANSWER[LANGUAGE],
                reply_markup=ReplyKeyboardRemove())

ANSWER_SUCCEDED = {
    'en' : "Your answer was submitted successfully!",
    'gr' : "Η απάντηση σας καταχωρήθηκε επιτυχώς!",
    'tr' : "Cevabınız başarıyla gönderildi!"
}

ANSWER_FAILED = {
    'en' : "Your answer could not be submitted. Please try again.",
    'gr' : "Η απάντηση σας δεν μπόρεσε να καταχωρηθεί. Παρακαλώ δοκιμάστε ξανά.",
    'tr' : "Cevabınız gönderilemedi. Lütfen yeniden deneyiniz."
}

def answer_handler(update: Update, context: CallbackContext):
    """
    Handles the answer typed by the user by sending it to the server.
    """
    DATA = context.user_data['question']
    MESSAGE = update.message
    USER = update.effective_user

    if (MESSAGE is not None):
        request = requests.post(f'{SERVER}/send_answer', data={
                'user_id' : USER.id,
                'question_id' : DATA['question_id'],
                'answer' : MESSAGE.text,
            }, verify=False)

        if (request.status_code == 200):
            MESSAGE.reply_text(ANSWER_SUCCEDED[context.chat_data['language']])
        else:
            MESSAGE.reply_text(ANSWER_FAILED[context.chat_data['language']])

    return ConversationHandler.END

NO_ASKED_QUESTIONS = {
    'en' : "Currently you do not have any active questions. You can ask using /ask_question",
    'gr' : "Προς το παρόν δεν έχετε ενεργές ερωτήσεις. Μπορείτε να ρωτήσετε χρησιμοποιώντας "
        "/ask_question",
    'tr' : "Şu an için aktif bir sorunuz yok. Şunu kullanarak sorabilirsiniz /ask_question"
}

ASKED_QUESTIONS = {
    'en' : r"_*__These are all the questions that you have asked\:__*""\n"
        r"\(by pressing a question, you can manage that question\)_""\n",
    'gr' : r"_*__Αυτές είναι όλες οι ερωτήσεις που έχετε κάνει\:__*""\n"
        r"\(πατώντας το μια ερώτηση, μπορείτε να τη διαχειριστείτε\)_""\n",
    'tr' : r"_*__Sormuş olduğunuz tüm sorular bunlar\:__*""\n"
        r"\(Soruların üzerine tıklayarak soruları yönetebilirsiniz\)_"
}

# FIXME Does not check if the user has submitted questions previously.
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
        
        for (index, question) in enumerate(questions):
            markup_list.append(InlineKeyboardButton(question['text'], callback_data={
                'button_id' : index,
                'question_id' : question['id'],
                'type' : 'asked'
            }.__str__()))
            result += f"{question['id']} - {question['text']}\n"
        
        message.reply_markdown_v2(ASKED_QUESTIONS[context.chat_data['language']],
            reply_markup=InlineKeyboardMarkup.from_column(markup_list))
        return 0

NO_ANSWER = {
    'en' : "No one has yet to answer.",
    'gr' : "Κανείς δεν έχει απαντήσει ακόμη.",
    'tr' : "Şu ana kadar kimse cevaplamadı."
}

SOLVED_SUCCEDED = {
    'en' : "The question was successfully marked as solved!",
    'gr' : "Η ερώτηση έχει επισημανθεί επιτυχώς ως λυμένη!",
    'tr' : "Soru çözüldü olarak işaretlendi!"
}

ERROR = {
    'en' : "An error occurred.",
    'gr' : "Παρουσιάστηκε κάποιο σφάλμα.",
    'tr' : "Bir hata oluştu."
}

def asked_question_manipulation(update: Update, context: CallbackContext):
    """
    This does handles the action that the user has selected from `selected_question_choice`. It either
    finds the answers or marks the question as solved.
    """
    DATA = context.user_data['question']
    MESSAGE = update.message
    MESSAGE_CONTENT = MESSAGE.text.lower()
    USER = update.effective_user

    if (MESSAGE is not None):   
        if (all(el in MESSAGE_CONTENT for el in ['see', 'answers'])) :
            request = requests.get(f'{SERVER}/question_answers', params={
                    'user_id' : USER.id,
                    'question_id' : DATA['question_id']
                }, verify=False)
                
            answers: list = request.json()['answers']
            result = ""

            for (index, answer) in enumerate(answers):
                result += f"{index + 1} - {answer['text']}\n"
            
            new_result = ""
            for character in result:
                if (character in string.punctuation):
                    new_result += f"\{character}"
                else:
                    new_result += character
            if (new_result == ""):
                MESSAGE.reply_text(NO_ANSWER[context.chat_data['language']], reply_markup=ReplyKeyboardRemove())
            else:
                MESSAGE.reply_markdown_v2(f'_{new_result}_', reply_markup=ReplyKeyboardRemove())
        elif ('mark as solved' in MESSAGE_CONTENT):
            request = requests.post(f'{SERVER}/mark_as_solved', data={
                'user_id' : USER.id,
                'question_id' : DATA['question_id']
            }, verify=False)
            
            if (request.status_code == 200):
                MESSAGE.reply_text(SOLVED_SUCCEDED[context.chat_data['language']],
                reply_markup=ReplyKeyboardRemove())
            else:
                MESSAGE.reply_text(ERROR[context.chat_data['language']], reply_markup=ReplyKeyboardRemove())
        else:
            MESSAGE.reply_text(NO_SUCH_ANSWER[context.chat_data['language']],
            reply_markup=ReplyKeyboardRemove())
    context.user_data
    return ConversationHandler.END

def login(update: Update, context: CallbackContext):
    message = update.message
    if (message is not None):
        update.message.reply_html(
            f'<a href="http://wenet.u-hopper.com/dev/hub/frontend/oauth/login?client_id={APP_ID}">Login to Wenet</a>')

PROCESS_STOPPED = {
    'en' : "The process was stopped.",
    'gr' : "Η διαδικασία σταμάτησε.",
    'tr' : "Süreç durduruldu."
}

SELECTED = {
    'en' : "You selected:",
    'gr' : "Επιλέξατε:",
    'tr' : "Senin seçtiğin:"
}

SEE_ANSWERS = {
    'en' : "See the answers",
    'gr' : "Δείτε τις απαντήσεις",
    'tr' : "Cevapları gör"
}

MARK_SOLVED = {
    'en' : "Mark as solved",
    'gr' : "Επισημάνετε ως λυμένο",
    'tr' : "Çözüldü olarak işaretle"
}
NOTHING = {
    'en' : "Nothing",
    'gr' : "Τίποτα",
    'tr' : "Hiçbirşey"
}

QUESTION_ABOUT_QUESTION = {
    'en' : "What would you like to know about this question?",
    'gr' : "Τι θα θέλατε να μάθετε για αυτή την ερώτηση;",
    'tr' : "Bu soru hakkında ne bilmek istiyorsun?"
}

ANSWER_ABOUT_QUESTION = {
    'en' : "Would you like to answer this question?",
    'gr' : "Θα θέλατε να απαντήσετε αυτή την ερώτηση;",
    'tr' : "Bu soruyu cevaplamak istiyormusun?"
}

YES = {
    'en' : "Yes",
    'gr' : "Ναι",
    'tr' : "Evet"
}

NO = {
    'en' : "No",
    'gr' : "Όχι",
    'tr' : "Hayır"
}

def stop(update: Update, context: CallbackContext):
    update.message.reply_text(PROCESS_STOPPED[context.chat_data['language']], reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def selected_question_choice(update: Update, context: CallbackContext):
    """
    Depending on the question that the user (submitter) selected, it shows the possible actions:
        - to see the answers
        - to mark the question as solved
        - or nothing 
    """
    QUERY = update.callback_query
    DATA = json.loads(QUERY.data.replace("'",'"'))
    MESSAGE = QUERY.message

    if (MESSAGE is not None):
        LANGUAGE = context.chat_data['language']
        TYPE = DATA['type']
        SELECTED_BUTTON = MESSAGE.reply_markup.inline_keyboard[DATA['button_id']][0].text
        if (any(x in SELECTED_BUTTON for x in string.punctuation)):
            new_string = ""
            for x in SELECTED_BUTTON:
                if (x in string.punctuation):
                    new_string += f"\{x}"
                else:
                    new_string += x
            SELECTED_BUTTON = new_string

        MESSAGE.edit_text(f"{SELECTED[LANGUAGE]} _*{SELECTED_BUTTON}*_",
                        reply_markup=None, parse_mode=ParseMode.MARKDOWN_V2)
        context.user_data['question'] = DATA

        if (TYPE == 'asked'):
            markup_list = [
                KeyboardButton(SEE_ANSWERS[LANGUAGE]),
                KeyboardButton(SEE_ANSWERS[LANGUAGE]),
                KeyboardButton(NOTHING[LANGUAGE])
            ]

            MESSAGE.reply_text(QUESTION_ABOUT_QUESTION[LANGUAGE],
                reply_markup=ReplyKeyboardMarkup.from_column(markup_list, one_time_keyboard=True))
        elif (TYPE == 'available'):
            markup_list = [
                KeyboardButton(YES[LANGUAGE]),
                KeyboardButton(NO[LANGUAGE])
            ]

            MESSAGE.reply_text(ANSWER_ABOUT_QUESTION[LANGUAGE],
                reply_markup=ReplyKeyboardMarkup.from_column(markup_list, one_time_keyboard=True))

def change_to_greek(update: Update, context: CallbackContext):
    MESSAGE = update.message

    if (MESSAGE is not None):
        context.chat_data['language'] = 'gr'
        context.bot.set_my_commands(commands=[
            BotCommand('help', HELP_INFORMATION['gr']),
            BotCommand('login', LOGIN_INFORMATION['gr']),
            BotCommand('ask_question', ASK_QUESTION_INFORMATION['gr']),
            BotCommand('available_questions', AVAILABLE_QUESTIONS_INFORMATION['gr']),
            BotCommand('asked_questions', ASKED_QUESTIONS_INFORMATION['gr']),
            BotCommand('stop', STOP_INFORMATION['gr'])])

        MESSAGE.reply_text("Η γλώσσα του συστήματος έχει αλλάξει σε Ελληνικά.")

def change_to_turkish(update: Update, context: CallbackContext):
    MESSAGE = update.message

    if (MESSAGE is not None):
        context.chat_data['language'] = 'tr'
        context.bot.set_my_commands(commands=[
            BotCommand('help', HELP_INFORMATION['tr']),
            BotCommand('login', LOGIN_INFORMATION['tr']),
            BotCommand('ask_question', ASK_QUESTION_INFORMATION['tr']),
            BotCommand('available_questions', AVAILABLE_QUESTIONS_INFORMATION['tr']),
            BotCommand('asked_questions', ASKED_QUESTIONS_INFORMATION['tr']),
            BotCommand('stop', STOP_INFORMATION['tr'])])

        MESSAGE.reply_text("Sistemin dili Türkçe olarak değişti.")

def change_to_english(update: Update, context: CallbackContext):
    MESSAGE = update.message

    if (MESSAGE is not None):
        context.chat_data['language'] = 'en'
        context.bot.set_my_commands(commands=[
            BotCommand('help', HELP_INFORMATION['en']),
            BotCommand('login', LOGIN_INFORMATION['en']),
            BotCommand('ask_question', ASK_QUESTION_INFORMATION['en']),
            BotCommand('available_questions', AVAILABLE_QUESTIONS_INFORMATION['en']),
            BotCommand('asked_questions', ASKED_QUESTIONS_INFORMATION['en']),
            BotCommand('stop', STOP_INFORMATION['en'])])
        MESSAGE.reply_text("The system's language has changed to English.")

# FIXME Change the handlers behaviour to accept both Greek and Turkish.
def main() -> None:
    bot = Bot(BOT_TOKEN)
    bot.set_my_commands(commands=[
        BotCommand('help', HELP_INFORMATION['en']),
        BotCommand('login', LOGIN_INFORMATION['en']),
        BotCommand('ask_question', ASK_QUESTION_INFORMATION['en']),
        BotCommand('available_questions', AVAILABLE_QUESTIONS_INFORMATION['en']),
        BotCommand('asked_questions', ASKED_QUESTIONS_INFORMATION['en']),
        BotCommand('stop', STOP_INFORMATION['en'])])
    updater = Updater(BOT_TOKEN, persistence=PicklePersistence('bot/data/bot_data'))
    dispatcher = updater.dispatcher

    stop_handlers = [
        CommandHandler('stop', stop),
        MessageHandler(Filters.regex('^[C|c]ancel.?$') | Filters.regex('^[D|d]one.?$'), stop),
    ]

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))

    dispatcher.add_handler(CommandHandler('gr', change_to_greek))
    dispatcher.add_handler(CommandHandler('tr', change_to_turkish))
    dispatcher.add_handler(CommandHandler('en', change_to_english))

    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('ask_question', ask_question)],
        states={
            0 : [MessageHandler(
                Filters.text &  ~(Filters.command | Filters.regex('^[D|d]one[.|$]')),
                ask_question_handler
            )]
        },
        fallbacks=stop_handlers
    ))
    dispatcher.add_handler(CallbackQueryHandler(selected_question_choice))
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('asked_questions', asked_questions)],
        states={
            0 : [MessageHandler(
                Filters.text & ~(Filters.regex('^[C|c]ancel.?$') | Filters.regex('^[D|d]one.?$') |
                Filters.regex('^[N|n]othing.?$') | Filters.regex('^[Α|α]κύρωση.?$') |
                Filters.regex('^[Τ|τ]έλος.?$') | Filters.regex('^[Τ|τ]ίποτα.?$')| Filters.command),
                asked_question_manipulation)]
        },
        fallbacks=[
            CommandHandler('stop', stop),
            MessageHandler(Filters.regex('^[C|c]ancel.?$') | Filters.regex('^[D|d]one.?$'), stop),
            MessageHandler(Filters.regex('^[N|n]othing.?$'), stop)
        ]
    ))

    AVAILABLE_QUESTIONS_TEXT_FILTERS = (Filters.command | Filters.regex('^[C|c]ancel.?$') |
        Filters.regex('^[D|d]one.?$') | Filters.regex('^[Α|α]κύρωση.?$') |
        Filters.regex('^[N|n]o.?$') | Filters.regex('^[Τ|τ]έλος.?$') | Filters.regex('"[Ό|ό]χι.?$'))
    
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('available_questions', available_questions)],
        states= {
            0 : [MessageHandler(Filters.text & ~AVAILABLE_QUESTIONS_TEXT_FILTERS,
            available_question_manipulation)],
            1 : [MessageHandler(Filters.text & ~AVAILABLE_QUESTIONS_TEXT_FILTERS, answer_handler)],
        },
        fallbacks=[
            CommandHandler('stop', stop),
            MessageHandler(AVAILABLE_QUESTIONS_TEXT_FILTERS, stop),
        ]
    ))
    dispatcher.add_handler(CommandHandler('login', login))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
