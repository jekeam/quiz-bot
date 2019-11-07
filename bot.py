import logging
import configparser 
import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters, PicklePersistence
from telegram.ext.callbackcontext import CallbackContext
from threading import Thread
import os
from emoji import emojize
from db import User
import time

def check_done(update, context):
    if str(context.user_data.get('question_num','0')) == '0':
        pass
    else:
        dene(update, context)
    

def start(update, context):
    if str(context.user_data.get('question_num','0')) == '0':
        if context.user_data.get('id'):
            print('user is exists: ' + str(context.user_data['id']))
        else:
            context.user_data['id'] = update.message.chat.id
        print('context.user_data: ' + str(context.user_data))
        
        update.message.reply_text(text='Привет, студент!',reply_markup=ReplyKeyboardRemove())
        
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
    else:
        dene(update, context)
            

def agree(update, context):
    print('agree start')
    print('agree context.user_data: ' + str(context.user_data))
    user = update.callback_query.from_user
    id = user.id
    first_name = user.first_name
    last_name = user.last_name
    username = user.username
    
    context.user_data['first_name'] = first_name
    context.user_data['last_name'] = last_name
    context.user_data['username'] =username
    print(context.user_data)
    
    user, created = User.get_or_create(id=id, first_name=first_name, last_name=last_name, username=username)
    print(str(user) + ', created: ' + str(created))
    update.callback_query.message.reply_text(text='Отлично! Напиши как тебя зовут.', callback_data=str(PHONE))
    
    return NAME
     
     
def name(update, context):
    print('name work start')
    print('name user_data: ' + str(context.user_data))
    
    client_name =  update.message.text
    
    if len(client_name) <= 2:
        update.message.reply_text('Я вас не понимаю, пожалуйста, попробуйте еще раз')
        return NAME
        
    User.update(client_name=client_name).where(User.id == context.user_data.get('id')).execute()
    print('name work end')
    
    reply_keyboard = [[KeyboardButton('Отправить мой телефон', request_contact=True)]]
    update.message.reply_text('Нажми «Отправить мой телефон»', reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
    
    return PHONE
    
    
def phone(update, context):
    print('phone start')
    print('phone user_data: ' + str(context.user_data))
    
    User.update(phone=update.message.contact.phone_number).where(User.id == context.user_data.get('id')).execute()
    update.message.reply_text(text='Напиши пожалуйста свою почту', reply_markup=ReplyKeyboardRemove())
    print('phone end')
    return EMAIL
    
    
def email(update, context):
    print('email start')
    print('email user_data: ' + str(context.user_data))
    
    client_email =  update.message.text
    if '@' not in client_email:
        update.message.reply_text('Я вас не понимаю, пожалуйста, попробуйте еще раз')
        return EMAIL
    
    User.update(email=client_email).where(User.id == context.user_data.get('id')).execute()
    
    keyboard = []
    keyboard.append([InlineKeyboardButton(text='ДА', callback_data=str(QUIZ))])
    reply_markup = InlineKeyboardMarkup(keyboard)   
            
    update.message.reply_text(text='Приятно познакомиться ' + emojize(':slightly_smiling_face:', use_aliases=True) + '\nИтак, 5 заданий и мерч твой!\nГотов начать?', reply_markup=reply_markup)
    
    print('email end')
    # context.user_data['quiz'] = 'start'
    return QUIZ    
    
    
def quiz(update, context):
    print('quiz start')
    print('quiz user_data: ' + str(context.user_data))
    
    choise = context.user_data.get('quiz', 'start')
    
    if choise == 'start':
        keyboard = []
        keyboard.append([InlineKeyboardButton(text='Технологии 👨‍💻', callback_data=('technologies'))])
        keyboard.append([InlineKeyboardButton(text='Офис 🏦', callback_data=('office'))])
        keyboard.append([InlineKeyboardButton(text='Отделение продаж 👩‍💼💰👨‍💼' + emojize(':slightly_smiling_face:', use_aliases=True), callback_data=('sales'))])
        
        reply_markup = InlineKeyboardMarkup(keyboard)   
        update.callback_query.message.reply_text(text='Выбери, что тебе больше всего нравится', reply_markup=reply_markup)
    
    print('quiz end')
    return QUIZ
    

def technologies(update, context):
    check_done(update, context)
    
    User.update(test_name='technologies').where(User.id == context.user_data.get('id')).execute()
    print('technologies start')
    print('technologies user_data: ' + str(context.user_data))
    
    question_num = context.user_data.get('question_num', '0')
    
    data = update.callback_query.data
    print('technologies data: ' + str(data))
    
    try:
        answer = data.split(':')[1]
    except:
        answer = context.user_data.get('answer', '')
    print('question_num:{}, answer: {}'.format(question_num, answer))
    
    if question_num in ('0', '1'):
        question_text = 'Эрудит заплатил за бутылку с пробкой 11 рублей. Бутылка стоит на 10 рублей дороже чем пробка. Сколько стоит пробка?'
        question_answers = [
            '1 руб.',
            '0.50 коп.',
            '0.25 коп.',
            '0.75 коп.',
        ]
        if question_num == '0':
            context.user_data['question_num'] = '1'
            
        if not answer:
            update.callback_query.message.reply_text('Отлично! Вступай в Наш канал @IT_Sber_EKB')
            time.sleep(1)
            
            keyboard = []
            for n, i in enumerate(question_answers):
                keyboard.append(InlineKeyboardButton(text=i, callback_data=('technologies:' + str(n))))
            reply_markup = InlineKeyboardMarkup([keyboard])
            update.callback_query.message.reply_text(text=question_text, reply_markup=reply_markup)
        else:
            update.callback_query.message.reply_text(text='Ваш ответ: *' + str(question_answers[int(answer)]) + ' *',  parse_mode=telegram.ParseMode.MARKDOWN)
            
            try:
                if answer == '1':
                    context.user_data['question_ok'] = int(context.user_data.get('question_ok', '0'))+1
            except:
                pass
            
            context.user_data['question_num'] = '2'
            question_num = '2'
            answer = ''
            
    if question_num in ('2'):
        question_text = 'Что означает – систематизированное (структурированное) хранилище информации?'
        question_answers = [
            'Склад информации',
            'База',
            'База данных',
            'Хранилище',
        ]
        
        if not answer:
            keyboard = []
            for n, i in enumerate(question_answers):
                keyboard.append([InlineKeyboardButton(text=i, callback_data=('technologies:' + str(n)))])
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.callback_query.message.reply_text(text=question_text, reply_markup=reply_markup)
        else:
            update.callback_query.message.reply_text(text='Ваш ответ: *' + str(question_answers[int(answer)]) + ' *',  parse_mode=telegram.ParseMode.MARKDOWN)
        
            try:
                if answer == '2':
                    context.user_data['question_ok'] = int(context.user_data.get('question_ok', '0'))+1
            except:
                pass
            
            context.user_data['question_num'] = '3'
            question_num = '3'
            answer = ''
            
    if question_num in ('3'):
        question_text = 'По типу связи между данными базы данных подразделяют на:\n\n' + \
        '1. Иерархические, сетевые, реляционные, объектно-ориентированные\n' + \
        '2. Компьютерные и персональные\n' + \
        '3. Модульные, модемные и сетевые\n' + \
        '4. Основные и дополнительные'
        question_answers = [
            '1',
            '2',
            '3',
            '4',
        ]
        
        if not answer:
            keyboard = []
            for n, i in enumerate(question_answers):
                keyboard.append(InlineKeyboardButton(text=i, callback_data=('technologies:' + str(n))))
            reply_markup = InlineKeyboardMarkup([keyboard])
            update.callback_query.message.reply_text(text=question_text, reply_markup=reply_markup)
        else:
            update.callback_query.message.reply_text(text='Ваш ответ: *' + str(question_answers[int(answer)]) + ' *',  parse_mode=telegram.ParseMode.MARKDOWN)
        
            try:
                if answer == '0':
                    context.user_data['question_ok'] = int(context.user_data.get('question_ok', '0'))+1
            except:
                pass
            
            context.user_data['question_num'] = '4'
            question_num = '4'
            answer = ''    
    
    if question_num in ('4'):
        question_text = 'С чего всегда начинается создание базы данных?\n\n' + \
        '1. С запуска компьютера и запуска программы просмотрщика баз данных\n' + \
        '2. С создания макета документа\n' + \
        '3. С собеседования и обсуждения проблемы построения базы данных\n' + \
        '4. С разработки структуры ее таблиц'
        question_answers = [
            '1',
            '2',
            '3',
            '4',
        ]
        
        if not answer:
            keyboard = []
            for n, i in enumerate(question_answers):
                keyboard.append(InlineKeyboardButton(text=i, callback_data=('technologies:' + str(n))))
            reply_markup = InlineKeyboardMarkup([keyboard])
            update.callback_query.message.reply_text(text=question_text, reply_markup=reply_markup)
        else:
            update.callback_query.message.reply_text(text='Ваш ответ: *' + str(question_answers[int(answer)]) + ' *',  parse_mode=telegram.ParseMode.MARKDOWN)
        
            try:
                if answer == '3':
                    context.user_data['question_ok'] = int(context.user_data.get('question_ok', '0'))+1
            except:
                pass
            
            context.user_data['question_num'] = '5'
            question_num = '5'
            answer = '' 
            
    if question_num in ('5'):
        question_text = 'Как расшифровывается SQL?\n\n1. structured question line\n2. structured query language\n3. strict question line\n4. strong question language'
        question_answers = [
            '1',
            '2',
            '3',
            '4',
        ]
        
        if not answer:
            keyboard = []
            for n, i in enumerate(question_answers):
                keyboard.append(InlineKeyboardButton(text=i, callback_data=('technologies:' + str(n))))
            reply_markup = InlineKeyboardMarkup([keyboard])
            update.callback_query.message.reply_text(text=question_text, reply_markup=reply_markup)
        else:
            update.callback_query.message.reply_text(text='Ваш ответ: *' + str(question_answers[int(answer)]) + ' *',  parse_mode=telegram.ParseMode.MARKDOWN)
        
            try:
                if answer == '1':
                    context.user_data['question_ok'] = int(context.user_data.get('question_ok', '0'))+1
            except:
                pass
            
            context.user_data['question_num'] = '6'
            question_num = '6'
            answer = ''
            
    if question_num in ('6'):
        dene(update, context)
    
    print('question_ok:' + str(context.user_data.get('question_ok')))
    return QUIZ
    
def dene(update, context):
    try:
        message = update.callback_query.message
    except:
        message = update.message
    message.reply_text(text='Вы ответили правильно на '+ str(context.user_data.get('question_ok')) + ' вопросов из 5!',  parse_mode=telegram.ParseMode.MARKDOWN)
    message.reply_text(text='Поздравляю! Ты завершил испытание! Подойти на стойку Сбербанка, покажи это сообщение, получи свой мерч и уникальный номер для розыгрыша рюкзака. Розыгрыш состоится в *19.00 и 20:30* на стенде Сбербанка. Удачи!',  parse_mode=telegram.ParseMode.MARKDOWN)
    
     
def office(update, context):
    check_done(update, context)
    
    User.update(test_name='office').where(User.id == context.user_data.get('id')).execute()
    print('office start')
    
    return QUIZ
     
     
def sales(update, context):
    check_done(update, context)
    
    User.update(test_name='sales').where(User.id == context.user_data.get('id')).execute()
    print('sales start')
    
    return QUIZ
    

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
    pp = PicklePersistence(filename='conversationbot')
    updater = Updater(token, use_context=True, persistence=pp, request_kwargs=REQUEST_KWARGS)
    dispatcher = updater.dispatcher
    context = CallbackContext(dispatcher)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            AGREE: [CallbackQueryHandler(agree, pattern='^' + str(AGREE) + '$')],
            NAME: [MessageHandler(Filters.text, name)],
            PHONE: [MessageHandler(Filters.contact, phone)],
            EMAIL: [MessageHandler(Filters.text, email)],
            QUIZ: [
                CallbackQueryHandler(quiz, pattern='^' + str(QUIZ) + '$'),
                CallbackQueryHandler(technologies, pattern='^technologies.*'),
                CallbackQueryHandler(office, pattern='^office$'),
                CallbackQueryHandler(quiz, pattern='^sales$'),
                ]
        },
        fallbacks=[CommandHandler('start', start)],
        name="my_conversation",
        persistent=True
    )

    dispatcher.add_handler(conv_handler)

    
    updater.start_polling()
    updater.idle()