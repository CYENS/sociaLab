import json
import logging
import string
import requests
import os

from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler, PicklePersistence

BOT_TOKEN = os.environ['BOT_TOKEN']

APP_ID = os.environ['APP_ID']
SERVER = os.environ['SERVER']
WENET_WEBSITE = os.environ['WENET_WEBSITE']
WENET_AUTHENTICATION = os.environ['WENET_AUTHENTICATION']

LOGIN_INFORMATION = {
    'en' : "login to your WeNet account and establish a connection with your Telegram account",
    'gr' : "συνδεθείτε στο λογαριασμό σας στο WeNet για να δημιουργήσετε μια σύνδεση με το λογαριασμό σας στο Telegram",
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

SOLVED_QUESTION_INFORMATION = {
    'en' : "shows all the solved questions that you asked and allows you to manipulate them",
    'gr' : "σας δείχνει όλες τις λυμένες ερωτήσεις που έχετε υποβάλει όπου μπορείτε να τις "
        "διαχειριστείτε",
    'tr' : "Sormuş olduğunuz tüm soruları gösterir ve üzerlerinde değişiklik yapmanıza izin verir"
}

STOP_INFORMATION = {
    'en' : r"allows you to stop/interrupt a process that you have started\. A process is started "\
        r"by using /ask\_question, /available\_questions, /asked\_questions and processes in them",
    'gr' : r"σας επιτρέπει να σταματήσετε τη διαδικασία που έχετε αρχίσει με μια από τις "\
        r"εντολές\: /ask\_question, /available\_questions και /asked\_questions",
    'tr' : r"Başlatmış olduğunuz süreci durdurmak/kesintiye uğratmak için size izin verir\. Süreç "\
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
        update.message.reply_markdown_v2(rf"*_Welcome to sociaLab\!_* The default language is "
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

AVAILABLE_COMMANDS = {
    'en' : "These are the available commands",
    'gr' : "Αυτές είναι οι διαθέσιμες αλλαγές",
    'tr' : "Mevcut olan komutlar bunlar"
}

def help(update: Update, context: CallbackContext):
    """
    Can be used by the user to print (text) them the available actions.
    """
    user = update.effective_user
    LANGUAGE = context.chat_data['language']

    update.message.reply_markdown_v2(
    rf"*{AVAILABLE_COMMANDS[LANGUAGE]}*\:""\n"
    rf"• /login \- _{LOGIN_INFORMATION[LANGUAGE]}_""\n"
    rf"• /ask\_question \- _{ASK_QUESTION_INFORMATION[LANGUAGE]}_""\n"
    rf"• /available\_questions \- _{AVAILABLE_QUESTIONS_INFORMATION[LANGUAGE]}_""\n"
    rf"• /asked\_questions \- _{ASKED_QUESTIONS_INFORMATION[LANGUAGE]}_""\n"
    rf"• /solved\_questions \- _{SOLVED_QUESTION_INFORMATION[LANGUAGE]}_""\n"
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

QUESTION_NOT_LOGGED_IN = {
    'en' : "Your question could not be submitted because you have not logged in yet.",
    'gr' : "Η ερώτηση σας δεν μπόρεσε να καταχωρηθεί επειδή δεν έχετε συνδεθεί ακόμη",
    'tr' : "Henüz giriş yapmadığınız için sorunuz iletilemedi"
}

def ask_question_handler(update: Update, context: CallbackContext):
    """
    Handles the question typed by the user by sending it to the server.
    """
    MESSAGE = update.message
    USER = update.effective_user

    if (MESSAGE is not None):
        request = requests.post(f'{SERVER}/ask_question', data={
                'user_id' : USER.id,
                'question' : MESSAGE.text,
            }, verify=False)

        if (request.status_code == 200):
            MESSAGE.reply_text(QUESTION_SUCCEDED[context.chat_data['language']])
        elif (request.status_code == 400):
            MESSAGE.reply_text(QUESTION_NOT_LOGGED_IN[context.chat_data['language']])
        else:
            MESSAGE.reply_text(QUESTION_FAILED[context.chat_data['language']])
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

AVAILABLE_QUESTIONS_NOT_LOGGED_IN = {
    'en' : "Your have to be logged in to see any available questions for you.",
    'gr' : "Πρέπει να είστε συνδεδεμένοι για να δείτε τυχόν διαθέσιμες ερωτήσεις για εσάς.",
    'tr' : "Sizin için herhangi bir soru olup olmadığını görmeniz için giriş yapmanız gerekir."
}

def available_questions(update: Update, context: CallbackContext):
    """
    Texts the user with the available (unsolved) questions that they have according to the WeNet 
    platform.
    """
    MESSAGE = update.message
    USER = update.effective_user

    if (MESSAGE != None):
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
            
            if (len(questions) == 0):
                MESSAGE.reply_text(NO_AVAILABLE_QUESTIONS[context.chat_data['language']])
            else:
                MESSAGE.reply_markdown_v2(AVAILABLE_QUESTIONS[context.chat_data['language']],
                    reply_markup=InlineKeyboardMarkup.from_column(markup_list))
                return 0
        else:
            MESSAGE.reply_text(AVAILABLE_QUESTIONS_NOT_LOGGED_IN[context.chat_data['language']])
        return ConversationHandler.END

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

ASKED_QUESTIONS_NOT_LOGGED_IN = {
    'en' : "You have to be logged in to see questions that you have asked.",
    'gr' : "Πρέπει να είστε συνδεδεμένοι για να δείτε ερωτήσεις που έχετε κάνει.",
    'tr' : "Sormuş olduğunuz soruları görebilmeniz için giriş yapmanız gerekir"
}

def asked_questions(update: Update, context: CallbackContext):
    """
    It can be used by a user to see their asked questions.
    """
    MESSAGE = update.message
    
    if (MESSAGE is not None):
        user = update.effective_user
        request = requests.get(f'{SERVER}/asked_questions', params={
            'user_id' : user.id
        }, verify=False)
        
        if (request.status_code == 200):
            questions: list = request.json()['questions']
            
            markup_list = []
            
            for (index, question) in enumerate(questions):
                markup_list.append(InlineKeyboardButton(question['text'], callback_data={
                    'button_id' : index,
                    'question_id' : question['id'],
                    'type' : 'asked'
                }.__str__()))
            
            if (len(questions) == 0):
                MESSAGE.reply_text(NO_ASKED_QUESTIONS[context.chat_data['language']])
            else:
                MESSAGE.reply_markdown_v2(ASKED_QUESTIONS[context.chat_data['language']],
                    reply_markup=InlineKeyboardMarkup.from_column(markup_list))
                return 0
        else:
            MESSAGE.reply_text(ASKED_QUESTIONS_NOT_LOGGED_IN[context.chat_data['language']])
        return ConversationHandler.END

NO_ANSWER = {
    'en' : "No one has yet to answer.",
    'gr' : "Κανείς δεν έχει απαντήσει ακόμη.",
    'tr' : "Şu ana kadar kimse cevaplamadı."
}

MARK_SOLVED_SUCCEDED = {
    'en' : "The question was successfully marked as solved!",
    'gr' : "Η ερώτηση έχει επισημανθεί επιτυχώς ως λυμένη!",
    'tr' : "Soru çözüldü olarak işaretlendi!"
}

MARK_SOLVED_FAILED = {
    'en' : "The question could not be marked as solved. Please try again.",
    'gr' : "Η ερώτηση δεν μπόρεσε να επισημανθεί ως λυμένη. Παρακαλώ δοκιμάστε ξανά.",
    'tr' : "Soru cevaplandı olarak işaretlenemedi. Lütfen tekrar deneyiniz."
}

ERROR = {
    'en' : "An error occurred.",
    'gr' : "Παρουσιάστηκε κάποιο σφάλμα.",
    'tr' : "Bir hata oluştu."
}

DELETE_QUESTION_SUCCEDED = {
    'en' : "The question was successfully deleted!",
    'gr' : "Η ερώτηση διαγράφτηκε με επιτυχία!",
    'tr' : "Soru başarılı bir şekilde silindi!"
}

DELETE_QUESTION_FAILED = {
    'en' : "The question could not be deleted. Please try again.",
    'gr' : "Η ερώτηση δεν μπόρεσε να διαγραφτεί. Παρακαλώ δοκιμάστε ξανά.",
    'tr' : "Soru silinemedi. Lütfen tekrar deneyiniz."
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
    LANGUAGE = context.chat_data['language']

    if (MESSAGE is not None):   
        if (SEE_ANSWERS[LANGUAGE].lower() in MESSAGE_CONTENT):
            request = requests.get(f'{SERVER}/question_answers', params={
                    'user_id' : USER.id,
                    'question_id' : DATA['question_id']
                }, verify=False)
                
            answers: list = request.json()['answers']
            if (len(answers) == 0):
                MESSAGE.reply_text(NO_ANSWER[LANGUAGE], reply_markup=ReplyKeyboardRemove())
            else:
                result = ""

                for (index, answer) in enumerate(answers):
                    result += f"{index + 1} - {answer['text']}\n"

                new_result = ""
                for character in result:
                    if (character in string.punctuation):
                        new_result += f"\{character}"
                    else:
                        new_result += character

                MESSAGE.reply_markdown_v2(f'_{new_result}_', reply_markup=ReplyKeyboardRemove())
        elif (MARK_SOLVED[LANGUAGE].lower() in MESSAGE_CONTENT):
            request = requests.post(f'{SERVER}/mark_as_solved', data={
                'user_id' : USER.id,
                'question_id' : DATA['question_id']
            }, verify=False)
            
            if (request.status_code == 200):
                MESSAGE.reply_text(MARK_SOLVED_SUCCEDED[LANGUAGE],
                reply_markup=ReplyKeyboardRemove())
            else:
                MESSAGE.reply_text(MARK_SOLVED_FAILED[LANGUAGE], reply_markup=ReplyKeyboardRemove())
        elif (DELETE_QUESTION[LANGUAGE].lower() in MESSAGE_CONTENT):
            request = requests.post(f'{SERVER}/delete_question', data={
                'user_id' : USER.id,
                'question_id' : DATA['question_id']
            })

            if (request.status_code == 200):
                MESSAGE.reply_text(DELETE_QUESTION_SUCCEDED[LANGUAGE],
                    reply_markup=ReplyKeyboardRemove())
            else:
                MESSAGE.reply_text(DELETE_QUESTION_FAILED[LANGUAGE],
                    reply_markup=ReplyKeyboardRemove())
        else:
            MESSAGE.reply_text(NO_SUCH_ANSWER[LANGUAGE],
            reply_markup=ReplyKeyboardRemove())
            return 0
    return ConversationHandler.END

NO_SOLVED_QUESTIONS = {
    'en' : "There are no solved questions.",
    'gr' : "Δεν υπάρχουν λυμένες ερωτήσεις",
    'tr' : "Cevaplanmış sorular yok."
}

SOLVED_QUESTIONS = {
    'en' : r"_*__These are all the questions that you have marked as solved\:__*""\n"
        r"\(by pressing a question, you can manage that question\)_""\n",
    'gr' : r"_*__Αυτές είναι όλες οι ερωτήσεις που έχετε επισημάνει ως λυμένες\:__*""\n"
        r"\(πατώντας το μια ερώτηση, μπορείτε να τη διαχειριστείτε\)_""\n",
    'tr' : r"_*__Cevaplandı olarak işaretlediğiniz tüm sorular bunlar\:__*""\n"
        r"\(Soruların üzerine tıklayarak soruları yönetebilirsiniz\)_""\n"
}

SOLVED_QUESTIONS_NOT_LOGGED_IN = {
    'en' : "You have to be logged in to see questions that you have marked as solved.",
    'gr' : "Πρέπει να είστε συνδεδεμένοι για να δείτε ερωτήσεις που έχετε επισημάνει ως λυμένες.",
    'en' : "Cevaplandı olarak işaretlediğiniz soruları görebilmeniz için giriş yapmanız gerekir."
}

def solved_questions(update: Update, context: CallbackContext):
    DATA = context.user_data['question']
    MESSAGE = update.message
    USER = update.effective_user
    LANGUAGE = context.chat_data['language']

    if (MESSAGE is not None):
        request = requests.get(f'{SERVER}/solved_questions', params={
            'user_id' : USER.id,
            'question_id' : DATA['question_id']
        })
        
        if (request.status_code == 200):
            questions = request.json()['questions']

            if (len(questions) == 0):
                MESSAGE.reply_text(NO_SOLVED_QUESTIONS[LANGUAGE])
            else:
                markup_list = []
                for (index, question) in enumerate(questions):
                    markup_list.append(InlineKeyboardButton(question['text'], callback_data={
                        'button_id' : index,
                        'question_id' : question['id'],
                        'type' : 'solved'
                    }.__str__()))
                
                MESSAGE.reply_markdown_v2(SOLVED_QUESTIONS[LANGUAGE],
                    reply_markup=InlineKeyboardMarkup.from_column(markup_list))
                return 0
        else:
            MESSAGE.reply_text(SOLVED_QUESTIONS_NOT_LOGGED_IN[LANGUAGE])
        return ConversationHandler.END

MARK_UNSOLVED = {
    'en' : "Mark as unsolved",
    'gr' : "Επισημάνετε ως άλυτο",
    'tr' : "Cevaplanmadı olarak işaretle."
}

MARK_UNSOLVED_SUCCEDED = {
    'en' : "The question was successfully marked as unsolved!",
    'gr' : "Η ερώτηση έχει επισημανθεί επιτυχώς ως άλυτη!",
    'tr' : "Soru cevaplanmadı olarak işaretlendi!"
}

MARK_UNSOLVED_FAILED = {
    'en' : "The question could not be marked as unsolved. Please try again.",
    'gr' : "Η ερώτηση δεν μπόρεσε να επισημανθεί ως άλυτη. Παρακαλώ δοκιμάστε ξανά.",
    'tr' : "Soru cevaplanmadı olarak işaretlenemedi. Lütfen tekrar deneyiniz."
}

def solved_question_manipulation(update: Update, context: CallbackContext):
    DATA = context.user_data['question']
    MESSAGE = update.message
    MESSAGE_CONTENT = MESSAGE.text.lower()
    USER = update.effective_user
    LANGUAGE = context.chat_data['language']

    if (MESSAGE is not None):
        if (SEE_ANSWERS[LANGUAGE].lower() in MESSAGE_CONTENT):
            request = requests.get(f'{SERVER}/question_answers', params={
                    'user_id' : USER.id,
                    'question_id' : DATA['question_id']
                }, verify=False)
                
            answers: list = request.json()['answers']
            if (len(answers) == 0):
                MESSAGE.reply_text(NO_ANSWER[LANGUAGE], reply_markup=ReplyKeyboardRemove())
            else:
                result = ""

                for (index, answer) in enumerate(answers):
                    result += f"{index + 1} - {answer['text']}\n"

                new_result = ""
                for character in result:
                    if (character in string.punctuation):
                        new_result += f"\{character}"
                    else:
                        new_result += character

                MESSAGE.reply_markdown_v2(f'_{new_result}_', reply_markup=ReplyKeyboardRemove())
        elif (MARK_UNSOLVED[LANGUAGE].lower() in MESSAGE_CONTENT):
            request = requests.post(f'{SERVER}/mark_as_unsolved', data={
                'question_id' : DATA['question_id']
            })
            
            if (request.status_code == 200):
                MESSAGE.reply_text(MARK_UNSOLVED_SUCCEDED[LANGUAGE],
                    reply_markup=ReplyKeyboardRemove())
            else:
                MESSAGE.reply_text(MARK_UNSOLVED_FAILED[LANGUAGE],
                    reply_markup=ReplyKeyboardRemove())
            
        elif (DELETE_QUESTION[LANGUAGE].lower() in MESSAGE_CONTENT):
            request = requests.post(f'{SERVER}/delete_question', data={
                'user_id' : USER.id,
                'question_id' : DATA['question_id']
            })

            if (request.status_code == 200):
                MESSAGE.reply_text(DELETE_QUESTION_SUCCEDED[LANGUAGE],
                    reply_markup=ReplyKeyboardRemove())
            else:
                MESSAGE.reply_text(DELETE_QUESTION_FAILED[LANGUAGE],
                    reply_markup=ReplyKeyboardRemove())
        else:
            MESSAGE.reply_text(NO_SUCH_ANSWER[LANGUAGE], reply_markup=ReplyKeyboardRemove())
            return 0
        return ConversationHandler.END


LOGIN = {
    'en' : "Login to WeNet",
    'gr' : "Συνδεθείτε στο WeNet",
    'tr' : "WeNet'e bağlan "
}

def login(update: Update, context: CallbackContext):
    """
    Sends to the user a link which will redirect them to WeNet's login/registration page, which will
    redirect them back to Telegram to create a connection between the two services.
    """
    MESSAGE = update.message
    if (MESSAGE is not None):
        MESSAGE.reply_html(
            f"<a href='{WENET_AUTHENTICATION}'>{LOGIN[context.chat_data['language']]}</a>")

# TODO Create another function, which allows the user to delete their account and all associated data.
def delete(update: Update, context: CallbackContext):
    """
    Allows the user to delete their account with an alert box to ensure their decision. All of their
     associated data will be delete from the server and telegram.
    """
    MESSAGE = update.message

    pass

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

QUESTION_ABOUT_ANSWER = {
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

DELETE_QUESTION = {
    'en' : "Delete",
    'gr' : "Διαγραφή",
    'tr' : "Sil"
}

def stop(update: Update, context: CallbackContext):
    """
    Used for interrupting any process began by a `ConversationHandler`.
    """
    update.message.reply_text(PROCESS_STOPPED[context.chat_data['language']], reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# FIXME Documentation
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
                KeyboardButton(MARK_SOLVED[LANGUAGE]),
                KeyboardButton(DELETE_QUESTION[LANGUAGE]),
                KeyboardButton(NOTHING[LANGUAGE])
            ]

            MESSAGE.reply_text(QUESTION_ABOUT_QUESTION[LANGUAGE],
                reply_markup=ReplyKeyboardMarkup.from_column(markup_list, one_time_keyboard=True))
        elif (TYPE == 'available'):
            markup_list = [
                KeyboardButton(YES[LANGUAGE]),
                KeyboardButton(NO[LANGUAGE])
            ]

            MESSAGE.reply_text(QUESTION_ABOUT_ANSWER[LANGUAGE],
                reply_markup=ReplyKeyboardMarkup.from_column(markup_list, one_time_keyboard=True))
        elif (TYPE == 'solved'):
            markup_list = [
                KeyboardButton(SEE_ANSWERS[LANGUAGE]),
                KeyboardButton(MARK_UNSOLVED[LANGUAGE]),
                KeyboardButton(DELETE_QUESTION[LANGUAGE]),
                KeyboardButton(NOTHING[LANGUAGE])
            ]
            MESSAGE.reply_text(QUESTION_ABOUT_QUESTION[LANGUAGE],
                reply_markup=ReplyKeyboardMarkup.from_column(markup_list, one_time_keyboard=True))

STANDARD_COMMANDS = [
    BotCommand('gr', "Για Ελληνικά"),
    BotCommand('tr', "Türkçe için"),
    BotCommand('en', "For English")
]

def change_to_greek(update: Update, context: CallbackContext):
    """
    Changes the default UI's language to Greek.
    """
    MESSAGE = update.message

    if (MESSAGE is not None):
        context.chat_data['language'] = 'gr'
        context.bot.set_my_commands(commands=STANDARD_COMMANDS + [
            BotCommand('help', HELP_INFORMATION['gr']),
            BotCommand('login', LOGIN_INFORMATION['gr']),
            BotCommand('ask_question', ASK_QUESTION_INFORMATION['gr']),
            BotCommand('available_questions', AVAILABLE_QUESTIONS_INFORMATION['gr']),
            BotCommand('asked_questions', ASKED_QUESTIONS_INFORMATION['gr']),
            BotCommand('solved_questions', SOLVED_QUESTION_INFORMATION['gr']),
            BotCommand('stop', STOP_INFORMATION['gr'])])

        MESSAGE.reply_text("Η γλώσσα του συστήματος έχει αλλάξει σε Ελληνικά.")

def change_to_turkish(update: Update, context: CallbackContext):
    """
    Changes the default UI's language to Turkish.
    """
    MESSAGE = update.message

    if (MESSAGE is not None):
        context.chat_data['language'] = 'tr'
        context.bot.set_my_commands(commands=STANDARD_COMMANDS + [
            BotCommand('help', HELP_INFORMATION['tr']),
            BotCommand('login', LOGIN_INFORMATION['tr']),
            BotCommand('ask_question', ASK_QUESTION_INFORMATION['tr']),
            BotCommand('available_questions', AVAILABLE_QUESTIONS_INFORMATION['tr']),
            BotCommand('asked_questions', ASKED_QUESTIONS_INFORMATION['tr']),
            BotCommand('solved_questions', SOLVED_QUESTION_INFORMATION['tr']),
            BotCommand('stop', STOP_INFORMATION['tr'])])

        MESSAGE.reply_text("Sistemin dili Türkçe olarak değişti.")

def change_to_english(update: Update, context: CallbackContext):
    """
    Changes the default UI's language to English.
    """
    MESSAGE = update.message

    if (MESSAGE is not None):
        context.chat_data['language'] = 'en'
        context.bot.set_my_commands(commands=STANDARD_COMMANDS + [
            BotCommand('help', HELP_INFORMATION['en']),
            BotCommand('login', LOGIN_INFORMATION['en']),
            BotCommand('ask_question', ASK_QUESTION_INFORMATION['en']),
            BotCommand('available_questions', AVAILABLE_QUESTIONS_INFORMATION['en']),
            BotCommand('asked_questions', ASKED_QUESTIONS_INFORMATION['en']),
            BotCommand('solved_questions', SOLVED_QUESTION_INFORMATION['en']),
            BotCommand('stop', STOP_INFORMATION['en'])])
        MESSAGE.reply_text("The system's language has changed to English.")

def main() -> None:
    bot = Bot(BOT_TOKEN)
    bot.set_my_commands(commands=STANDARD_COMMANDS + [
        BotCommand('help', HELP_INFORMATION['en']),
        BotCommand('login', LOGIN_INFORMATION['en']),
        BotCommand('ask_question', ASK_QUESTION_INFORMATION['en']),
        BotCommand('available_questions', AVAILABLE_QUESTIONS_INFORMATION['en']),
        BotCommand('asked_questions', ASKED_QUESTIONS_INFORMATION['en']),
        BotCommand('solved_questions', SOLVED_QUESTION_INFORMATION['en']),
        BotCommand('stop', STOP_INFORMATION['en']),])
    updater = Updater(BOT_TOKEN, persistence=PicklePersistence('bot/data/bot_data'))
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))

    dispatcher.add_handler(CommandHandler('gr', change_to_greek))
    dispatcher.add_handler(CommandHandler('tr', change_to_turkish))
    dispatcher.add_handler(CommandHandler('en', change_to_english))

    ASK_QUESTION_TEXT_FILTERS = (Filters.command | Filters.regex('^[C|c]ancel.?$') |
        Filters.regex('^[D|d]one.?$') | Filters.regex('^[Α|α]κύρωση.?$') |
        Filters.regex('^[Τ|τ]έλος.?$') | Filters.regex('^[Y|y]apıldı.?$') |
        Filters.regex('^[İ|i]ptal.?$'))

    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('ask_question', ask_question)],
        states={
            0 : [MessageHandler(Filters.text &  ~ASK_QUESTION_TEXT_FILTERS, ask_question_handler)]
        },
        fallbacks=[
            CommandHandler('stop',stop),
            MessageHandler(ASK_QUESTION_TEXT_FILTERS, stop)
        ]
    ))

    ASKED_QUESTIONS_TEXT_FILTERS = (Filters.command | Filters.regex('^[C|c]ancel.?$') |
        Filters.regex('^[D|d]one.?$') | Filters.regex('^[N|n]othing.?$') |
        Filters.regex('^[Α|α]κύρωση.?$') | Filters.regex('^[Τ|τ]έλος.?$') |
        Filters.regex('^[Τ|τ]ίποτα.?$')  | Filters.regex('^[Y|y]apıldı.?$') |
        Filters.regex('^[İ|i]ptal.?$') | Filters.regex('^[H|h]içbirşey.?$'))

    dispatcher.add_handler(CallbackQueryHandler(selected_question_choice))
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('asked_questions', asked_questions)],
        states={
            0 : [MessageHandler(Filters.text & ~ASKED_QUESTIONS_TEXT_FILTERS,
                asked_question_manipulation)]
        },
        fallbacks=[
            CommandHandler('stop', stop),
            MessageHandler(ASKED_QUESTIONS_TEXT_FILTERS, stop)
        ]
    ))

    AVAILABLE_QUESTIONS_TEXT_FILTERS = (Filters.command | Filters.regex('^[C|c]ancel.?$') |
        Filters.regex('^[D|d]one.?$') | Filters.regex('^[N|n]o.?$') |
        Filters.regex('^[Α|α]κύρωση.?$') | Filters.regex('^[Τ|τ]έλος.?$') |
        Filters.regex('"[Ό|ό]χι.?$') | Filters.regex('^[Y|y]apıldı.?$') |
        Filters.regex('^[İ|i]ptal.?$') | Filters.regex('^[H|h]ayır].?$'))
    
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
    
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('solved_questions', solved_questions)],
        states={
            0 : [MessageHandler(Filters.text & ~ASKED_QUESTIONS_TEXT_FILTERS,
                solved_question_manipulation)],
        },
        fallbacks=[
            CommandHandler('stop', stop),
            MessageHandler(ASKED_QUESTIONS_TEXT_FILTERS, stop)
        ]
    ))
    dispatcher.add_handler(CommandHandler('login', login))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
