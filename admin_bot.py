from config import TOKEN_ADMIN_BOT as TOKEN
from models.database import Session
from sqlalchemy import and_
from telebot import types

import telebot

from models.user import User
from models.user_info import UserInfo
from models.product import Product
from models.offer import Offer
from models.notification import Notification


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start_command(message):
    msg = bot.send_message(message.chat.id,
                           'Это бот для администрирования Портала Поставщиков. Введите логин и пароль через пробел.')
    bot.register_next_step_handler(msg, auth)


def include_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    products_button = types.KeyboardButton('Проверка СТЕ')
    users_button = types.KeyboardButton('Поиск пользователей')
    info_button = types.KeyboardButton('Личный кабинет')
    markup.row(products_button)
    markup.row(users_button)
    markup.row(info_button)
    return markup


def remove_menu():
    markup = types.ReplyKeyboardRemove()
    return markup


def print_info(message):
    session = Session()
    answer = session.query(Product).filter(Product.is_confirmed == 0).count()
    bot.send_message(message.chat.id, f'Количестово неподтверждённых СТЕ: {answer}')
    session.close()


def print_product(message):
    session = Session()
    response = session.query(Product).filter(Product.is_confirmed == 0).all()
    session.close()

    if response:
        data = str(response[0]).split(', ')
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton('Принять', callback_data='confirm-product|' + data[0]),
            telebot.types.InlineKeyboardButton('Отклонить', callback_data='reject-product|' + data[0])
        )
        bot.send_message(message.chat.id,
                         f'ID поставщика: {data[1]}\nНазвание СТЕ: {data[2]}\nКатегория: {data[3]}\nКод КПГЗ: {data[4]}\nЦена за ед.: {data[6]}',
                         reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Нет неподтверждённых СТЕ.')


def print_user(message):
    session = Session()
    message_length = len(message.text)

    if message_length == 9:
        answer = session.query(UserInfo).filter(UserInfo.CRR == message.text).all()
    elif message_length == 10 or message_length == 12:
        answer = session.query(UserInfo).filter(UserInfo.ITN == message.text).all()
    else:
        answer = session.query(UserInfo).filter(UserInfo.user_id == message.text).all()

    if answer:
        answer = str(answer[0]).split(', ')
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton('Оповестить', callback_data='notify-user|' + answer[0]),
            telebot.types.InlineKeyboardButton('Удалить', callback_data='delete-user|' + answer[0])
        )
        bot.send_message(message.chat.id,
                         f'ID пользователя: {answer[0]}\nФИО: {answer[1]} {answer[2]} {answer[3]}\nРоль: {answer[4]}\nВид лица: {answer[5]}\nИНН: {answer[7]}',
                         reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Пользователь не найден.', reply_markup=include_main_menu())

    session.close()


def auth(message):
    try:
        data = message.text.split()
        session = Session()
        answer = session.query(User).filter(and_(User.login == data[0]),
                                            (User.password == data[1]),
                                            User.is_admin).all()
        session.close()
    except:
        answer = None

    if answer:
        bot.send_message(message.chat.id, 'Успешная авторизация.', reply_markup=include_main_menu())

    else:
        bot.send_message(message.chat.id, 'Неправильный логин или пароль.')
        msg = bot.send_message(message.chat.id, 'Введите логин и пароль через пробел.')
        bot.register_next_step_handler(msg, auth)


def confirm_product(message, id):
    session = Session()
    response = session.query(Product).get(id)
    response.is_confirmed = 1
    session.add(response)
    session.commit()
    session.close()

    print_product(message)


def reject_product(message, id):
    session = Session()
    response = session.query(Product).get(id)
    session.delete(response)
    session.commit()
    session.close()

    print_product(message)


def notify_user(message, id):
    session = Session()
    notify = Notification(
        user_id = id,
        title = "От модерации",
        description = message.text,
        is_viewed = 0
    )
    session.add(notify)
    session.commit()
    session.close()

    bot.send_message(message.chat.id, 'Оповещение добавлено.', reply_markup=include_main_menu())


def delete_user(message, id):
    session = Session()
    response = session.query(User).get(id)
    session.delete(response)
    session.commit()
    session.close()

    bot.send_message(message.chat.id, 'Пользователь удалён.', reply_markup=include_main_menu())


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == 'личный кабинет':
        print_info(message)
    elif message.text.lower() == 'поиск пользователей':
        msg = bot.send_message(message.chat.id, 'Введите ИНН, КПП или id пользователя.', reply_markup=remove_menu())
        bot.register_next_step_handler(msg, print_user)
    elif message.text.lower() == 'проверка сте':
        print_product(message)
    else:
        bot.send_message(message.chat.id, 'Неизвестная команда')


@bot.callback_query_handler(func=lambda call: True)
def query_handler(query):
    data = query.data
    message = query.message
    id = data[data.find("|") + 1:]

    if data.startswith('confirm-product|'):
        confirm_product(message, id)
        bot.answer_callback_query(query.id, "Продукт принят")
    elif data.startswith('reject-product|'):
        reject_product(message, id)
        bot.answer_callback_query(query.id, "Продукт отклонён")
    elif data.startswith('notify-user|'):
        msg = bot.send_message(message.chat.id, 'Напишите сообщение пользователю.')
        bot.register_next_step_handler(msg, notify_user, id)
    elif data.startswith('delete-user|'):
        delete_user(message, id)


bot.polling(none_stop=True)
