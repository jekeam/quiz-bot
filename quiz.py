import logging
import configparser 
import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
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
            
            keyboard.append([InlineKeyboardButton(text=emojize(':heavy_check_mark:', use_aliases=True) + agree_btn, callback_data='agree')])
            reply_markup = InlineKeyboardMarkup(keyboard)   
            
            doc = open(agree, 'rb')
            context.bot.send_document(update.message.chat.id, doc)
            doc.close()
            update.message.reply_text(text=agree_msq, reply_markup=reply_markup)
            

def callback_query_handler(update, context):
    if update.callback_query.data == 'agree':
         user = update.callback_query.from_user
         id = user.id
         first_name = user.first_name
         last_name = user.last_name
         username = user.username
         print('id:{}, first_name:{}, last_name: {}, username: {}'.format(id, first_name, last_name, username))
         user, created = User.get_or_create(id=id, first_name=first_name, last_name=last_name, username=username)
         print(user)
         print(created)

if __name__=="__main__":
    
    logging.basicConfig(filename='bot.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)
    # logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)
    
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

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(callback_query_handler))
    updater.start_polling()
    updater.idle()