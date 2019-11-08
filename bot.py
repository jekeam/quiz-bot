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
    qn = context.user_data.get('question_num','0')
    print(qn)
    if str(qn) != '6':
        pass
    else:
        done_send(update, context)
        return 'DONE'
    

def start(update, context):
    if check_done(update, context) == 'DONE':
        return DONE
    
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
    # else:
    #     done(update, context)
            

def agree(update, context):
    print('agree start')
    print('agree context.user_data: ' + str(context.user_data))
    check_done(update, context)
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
    check_done(update, context)
    client_name =  update.message.text
    
    if len(client_name) < 2:
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
    check_done(update, context)
    User.update(phone=update.message.contact.phone_number).where(User.id == context.user_data.get('id')).execute()
    update.message.reply_text(text='Напиши пожалуйста свою почту', reply_markup=ReplyKeyboardRemove())
    print('phone end')
    return EMAIL
    
    
def email(update, context):
    print('email start')
    print('email user_data: ' + str(context.user_data))
    check_done(update, context)
    client_email =  update.message.text
    if '@' not in client_email:
        update.message.reply_text('Я вас не понимаю, пожалуйста, попробуйте еще раз')
        return EMAIL
    
    User.update(email=client_email).where(User.id == context.user_data.get('id')).execute()
    
    keyboard = []
    answer = 'ДА'
    keyboard.append([InlineKeyboardButton(text=answer, callback_data='q1')])
    reply_markup = InlineKeyboardMarkup(keyboard)   
            
    update.message.reply_text(text='Приятно познакомиться ' + emojize(':slightly_smiling_face:', use_aliases=True) + '\nИтак, 5 заданий и мерч твой!\nГотов начать?', reply_markup=reply_markup)
    
    print('email end')
    context.user_data['answer'] = answer
    return QUIZ
    
    
# def quiz(update, context):
#     print('quiz start')
#     print('quiz user_data: ' + str(context.user_data))
    
#     choise = context.user_data.get('quiz', 'start')
    
#     if choise == 'start':
#         keyboard = []
#         keyboard.append([InlineKeyboardButton(text='Технологии 👨‍💻', callback_data=('technologies'))])
#         keyboard.append([InlineKeyboardButton(text='Офис 🏦', callback_data=('office'))])
#         keyboard.append([InlineKeyboardButton(text='Работа с клиентами 👩‍💼💰👨‍💼' + emojize(':slightly_smiling_face:', use_aliases=True), callback_data=('sales'))])
        
#         reply_markup = InlineKeyboardMarkup(keyboard)   
#         update.callback_query.message.reply_text(text='Выбери, что тебе больше всего нравится', reply_markup=reply_markup)
    
#     print('quiz end')
#     return QUIZ


def subcrible(update):
    update.callback_query.message.reply_text(text='Отлично! Вступай в Наш канал @IT_Sber_EKB', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='Подписаться', url="t.me/IT_Sber_EKB")]]))
    

def q1(update, context):
    check_done(update, context)
    update.callback_query.message.edit_text(text=update.callback_query.message.text + '\n\n - ' + str(context.user_data.get('answer', '')),  parse_mode=telegram.ParseMode.MARKDOWN)
    
    question_text = 'Эрудит заплатил за бутылку с пробкой 11 рублей. Бутылка стоит на 10 рублей дороже чем пробка. Сколько стоит пробка?'
    question_answers = [
        '1 рубль',
        '50 копеек',
        '25 копеек',
        '75 копеек',
    ]

    subcrible(update)
    
    keyboard = []
    for n, i in enumerate(question_answers):
        keyboard.append(InlineKeyboardButton(text=i, callback_data=('q2:' + str(n))))
    reply_markup = InlineKeyboardMarkup([keyboard])
    update.callback_query.message.reply_text(text=question_text, reply_markup=reply_markup)
    context.user_data['question_num'] = '1'
            
def q2(update, context):
    check_done(update, context)
    question_answers = [
        '1 рубль',
        '50 копеек',
        '25 копеек',
        '75 копеек',
    ]
    answer = update.callback_query.data.split(':')[1]
        
    update.callback_query.message.edit_text(text=update.callback_query.message.text + '\n\nВаш ответ: *' + str(question_answers[int(answer)]) + ' *',  parse_mode=telegram.ParseMode.MARKDOWN)

    if answer == '1':
        context.user_data['question_ok'] = '1'
    
    question_text = 'Послезавтра ты выходишь на стажировку в Сбербанк. Скажи в какой именно день недели ты начнешь стажироваться, если три дня назад был день, предшествующий понедельнику?'
    question_answers = [
        'Воскресенье',
        'Среда',
        'Четверг',
        'Пятница',
    ]
    keyboard = []
    for n, i in enumerate(question_answers):
        keyboard.append([InlineKeyboardButton(text=i, callback_data=('q3:' + str(n)))])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.reply_text(text=question_text, reply_markup=reply_markup)
    context.user_data['question_num'] = '2'
            
def q3(update, context):
    check_done(update, context)
    question_answers = [
        'Воскресенье',
        'Среда',
        'Четверг',
        'Пятница',
    ]
    answer = update.callback_query.data.split(':')[1]
        
    update.callback_query.message.edit_text(text=update.callback_query.message.text + '\n\nВаш ответ: *' + str(question_answers[int(answer)]) + ' *',  parse_mode=telegram.ParseMode.MARKDOWN)

    if answer == '3':
        context.user_data['question_ok'] = int(context.user_data.get('question_ok', '0'))+1
    
    question_text = 'Лист бумаги прямоугольной формы перегнули пополам шесть раз. В средней части этого сложенного листа просверлили насквозь два отверстия. Сколько отверстий можно будет насчитать на листе после его разворачивания в исходное положение?'
    question_answers = [
        '64',
        '128',
        '264',
        '12',
    ]
    

    keyboard = []
    for n, i in enumerate(question_answers):
        keyboard.append(InlineKeyboardButton(text=i, callback_data=('q4:' + str(n))))
    reply_markup = InlineKeyboardMarkup([keyboard])
    update.callback_query.message.reply_text(text=question_text, reply_markup=reply_markup)
    context.user_data['question_num'] = '3'
            
def q4(update, context):
    check_done(update, context)
    question_answers = [
        '64',
        '128',
        '264',
        '12',
    ]
    answer = update.callback_query.data.split(':')[1]
        
    update.callback_query.message.edit_text(text=update.callback_query.message.text + '\n\nВаш ответ: *' + str(question_answers[int(answer)]) + ' *',  parse_mode=telegram.ParseMode.MARKDOWN)
    
    if answer == '1':
        context.user_data['question_ok'] = int(context.user_data.get('question_ok', '0'))+1
    
    question_text = 'Ты бежишь дистанцию на Зеленом марафоне. Ты обогнал бегуна, занимавшего вторую позицию. Какую позицию ты сейчас занимаешь?'
    question_answers = [
        'Первую',
        'Вторую',
    ]
    
    keyboard = []
    for n, i in enumerate(question_answers):
        keyboard.append(InlineKeyboardButton(text=i, callback_data=('q5:' + str(n))))
    reply_markup = InlineKeyboardMarkup([keyboard])
    update.callback_query.message.reply_text(text=question_text, reply_markup=reply_markup)
    context.user_data['question_num'] = '4'
            
def q5(update, context):
    check_done(update, context)
    question_answers = [
        'Первую',
        'Вторую',
    ]
    answer = update.callback_query.data.split(':')[1]
        
    update.callback_query.message.edit_text(text=update.callback_query.message.text + '\n\nВаш ответ: *' + str(question_answers[int(answer)]) + ' *',  parse_mode=telegram.ParseMode.MARKDOWN)
    
    if answer == '1':
        context.user_data['question_ok'] = int(context.user_data.get('question_ok', '0'))+1
    
    question_text = 'Раздели 30 на ½ и прибавь 10. Какое число получится?'
    question_answers = [
        '15',
        '45',
        '85',
        '70',
    ]
    
    keyboard = []
    for n, i in enumerate(question_answers):
        keyboard.append(InlineKeyboardButton(text=i, callback_data=('q6:' + str(n))))
    reply_markup = InlineKeyboardMarkup([keyboard])
    update.callback_query.message.reply_text(text=question_text, reply_markup=reply_markup)
    context.user_data['question_num'] = '5'
    
    
def q6(update, context):

    question_answers = [
        '15',
        '45',
        '85',
        '70',
    ]
    answer = update.callback_query.data.split(':')[1]
        
    update.callback_query.message.edit_text(text=update.callback_query.message.text + '\n\nВаш ответ: *' + str(question_answers[int(answer)]) + ' *',  parse_mode=telegram.ParseMode.MARKDOWN)
    
    if answer == '3':
        context.user_data['question_ok'] = int(context.user_data.get('question_ok', '0'))+1
    done_send(update, context)
    return DONE
    
    
def done_send(update, context):
    try:
        message = update.callback_query.message
    except:
        message = update.message
    message.reply_text(text='Вы ответили правильно на '+ str(context.user_data.get('question_ok', '0')) + ' вопросов из 5!',  parse_mode=telegram.ParseMode.MARKDOWN)
    message.reply_text(text='Поздравляю! 🎉 Испытание пройдено! Подойти на стойку Сбербанка, покажи это сообщение, получи свой мерч и уникальный номер для розыгрыша рюкзака. Розыгрыш состоится в *19.00 и 20:30* на стенде Сбербанка. Удачи!',  parse_mode=telegram.ParseMode.MARKDOWN)
    context.user_data['question_num'] = '6'

if __name__=='__main__':
    
    logging.basicConfig(filename='bot.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR)
    # logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    AGREE, NAME, PHONE, EMAIL, QUIZ, DONE = range(6)
    
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
                CallbackQueryHandler(q1, pattern='^q1$'),
                CallbackQueryHandler(q2, pattern='^q2:\d$'),
                CallbackQueryHandler(q3, pattern='^q3:\d$'),
                CallbackQueryHandler(q4, pattern='^q4:\d$'),
                CallbackQueryHandler(q5, pattern='^q5:\d$'),
                CallbackQueryHandler(q6, pattern='^q6:\d$'),
                ],
            DONE: [
                CallbackQueryHandler(done_send, pattern='^DONE$'),
            ]
        },
        fallbacks=[CommandHandler('start', start)],
        name="my_conversation",
        persistent=True
    )

    dispatcher.add_handler(conv_handler)

    
    updater.start_polling()
    updater.idle()