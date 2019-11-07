import logging
import configparser 
import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
from telegram.ext.callbackcontext import CallbackContext
from threading import Thread
import os
from emoji import emojize
from db import User

def start(update, context):
    keyboard = []
    
    update.message.reply_text(config['message']['start'])
    
    agree = config['message']['agree']
    agree_msq = config['message']['agree_msq']
    agree_btn = config['message']['agree_btn']
    if agree and agree_msq and agree_btn:
        if os.path.isfile(agree):
            
            keyboard.append([InlineKeyboardButton(text=emojize(':heavy_check_mark:', use_aliases=True) + agree_btn, callback_data=str(AGREE))])
            reply_markup = InlineKeyboardMarkup(keyboard)   
            
            doc = open(agree, 'rb')
            context.bot.send_document(update.message.chat.id, doc)
            doc.close()
            update.message.reply_text(text=agree_msq, reply_markup=reply_markup)
    
    return AGREE
            

def agree(update, context):
     user = update.callback_query.from_user
     id = user.id
     first_name = user.first_name
     last_name = user.last_name
     username = user.username
     
     print('id:{}, first_name:{}, last_name: {}, username: {}'.format(id, first_name, last_name, username))
     
     user, created = User.get_or_create(id=id, first_name=first_name, last_name=last_name, username=username)
     update.callback_query.message.reply_text(text='Отлично! Напиши как тебя зовут.', callback_data=str(PHONE))
    
     return NAME
     
     
def name(update, context):
    print('name work start')
    print('name work end')
    
    reply_keyboard = [[KeyboardButton('Отправить мой телефон', request_contact=True)]]
    update.message.reply_text('Нажми «Отправить мой телефон»', reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    
    return PHONE
    
    
def phone(update, context):
    print('phone work start')
    print('phone work end')
    
    update.message.reply_text(text='Напиши пожалуйста свою почту', reply_markup=ReplyKeyboardRemove())
    return EMAIL
    
    
def email(update, context):
    print('email work start')
    print('email work end')
    
    keyboard = []
    keyboard.append([InlineKeyboardButton(text='ДА', callback_data=str(QUIZ))])
    reply_markup = InlineKeyboardMarkup(keyboard)   
            
    update.message.reply_text(text='Приятно познакомиться ' + emojize(':simple_smile:', use_aliases=True) + '\nИтак, 5 заданий и мерч твой!\nГотов начать?', reply_markup=reply_markup)
    
    return QUIZ    
    
    
def quiz(update, context):
    print('quiz work start')
    print('quiz work end')

if __name__=='__main__':
    
    logging.basicConfig(filename='bot.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)
    # logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    AGREE, NAME, PHONE, EMAIL, QUIZ = range(5)
    
    config = configparser.ConfigParser()
    config.read('quiz.ini')
    
    token = config['bot']['token']
    proxy = config['bot']['proxy']
    
    REQUEST_KWARGS = {
        'proxy_url': proxy,
        'read_timeout': 60,
        'connect_timeout': 30
    }
    
    updater = Updater(token, use_context=True, request_kwargs=REQUEST_KWARGS)
    dispatcher = updater.dispatcher
    context = CallbackContext(dispatcher)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            AGREE: [CallbackQueryHandler(agree, pattern='^' + str(AGREE) + '$')],
            NAME: [MessageHandler(Filters.text, name)],
            PHONE: [MessageHandler(Filters.contact, phone)],
            EMAIL: [MessageHandler(Filters.text, email)],
            QUIZ: [CallbackQueryHandler(quiz, pattern='^' + str(QUIZ) + '$')]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    dispatcher.add_handler(conv_handler)

    
    updater.start_polling()
    updater.idle()