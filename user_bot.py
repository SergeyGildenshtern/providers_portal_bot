from config import TOKEN_USER_BOT as TOKEN
from models.database import Session
from sqlalchemy import not_, and_, desc
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
                           'Это бот для закупок и продаж на Портале Поставщиков. Введите логин и пароль через пробел.',
                           reply_markup=remove_menu())
    bot.register_next_step_handler(msg, auth)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    message.text = message.text.lower()
    if message.text == 'поиск сте':
        msg = bot.send_message(message.chat.id, 'Введите название или категорию СТЕ', reply_markup=remove_menu())
        bot.register_next_step_handler(msg, search_products)
    elif message.text == 'личный кабинет':
        bot.send_message(message.chat.id, 'Выберите действие', reply_markup=include_personal_information_menu())
    elif message.text == 'мои данные':
        print_user_information(message)
    elif message.text == 'уведомления':
        print_user_notifications(message)
    elif message.text == 'назад':
        bot.send_message(message.chat.id, 'Выберите действие', reply_markup=include_main_menu())
    else:
        bot.send_message(message.chat.id, 'Неизвестная команда')


@bot.callback_query_handler(func=lambda call: True)
def query_handler(query):
    data = query.data
    message = query.message
    id = data[data.find("|") + 1:]

    if data.startswith('create-product|'):
        msg = bot.send_message(message.chat.id, 'Введите вашу цену за еденицу товара')
        bot.register_next_step_handler(msg, create_product, id)
    elif data.startswith('buy-product|'):
        msg = bot.send_message(message.chat.id, 'Введите количество покупаемого товара')
        bot.register_next_step_handler(msg, buy_product, id)


def auth(message):
    try:
        data = message.text.split()
        session = Session()
        response = session.query(User).filter(and_(User.login == data[0]),
                                              (User.password == data[1]),
                                              (User.is_admin == 0)).all()
        session.close()
    except:
        response = None

    if response:
        response = convert_record_to_list(response[0])

        session = Session()
        response2 = session.query(User).get(response[0])
        response2.telegram_chat_id = message.chat.id
        session.add(response2)
        session.commit()
        session.close()

        bot.send_message(message.chat.id, 'Успешная авторизация', reply_markup=include_main_menu())
    else:
        bot.send_message(message.chat.id, 'Неправильный логин или пароль')
        msg = bot.send_message(message.chat.id, 'Введите логин и пароль через пробел')
        bot.register_next_step_handler(msg, auth)


def convert_record_to_list(record):
    return str(record).split(', ')


def include_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    products_button = types.KeyboardButton('Поиск СТЕ')
    info_button = types.KeyboardButton('Личный кабинет')
    markup.row(products_button, info_button)
    return markup


def include_personal_information_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    info_button = types.KeyboardButton('Мои данные')
    notifications_button = types.KeyboardButton('Уведомления')
    back_button = types.KeyboardButton('Назад')

    markup.row(info_button, notifications_button)
    markup.row(back_button)
    return markup


def remove_menu():
    markup = types.ReplyKeyboardRemove()
    return markup


def print_user_information(message):
    session = Session()
    response = session.query(User, UserInfo).join(UserInfo).filter(User.telegram_chat_id == message.chat.id).all()
    session.close()
    response = convert_record_to_list(response[0])
    bot.send_message(message.chat.id, f'Фамилия: {response[6]}\nИмя: {response[7]}\nОтчество: {response[8]}\n'
                                      f'Вид лица: {response[10]}\nИНН: {response[12]}\n'
                                      f'КПП: {response[13][:-2] if response[13] != "None)" else "------------------"}')


def print_user_notifications(message):
    session = Session()
    response = session.query(User, Notification).join(Notification) \
        .filter(and_((User.telegram_chat_id == message.chat.id),
                     (Notification.is_viewed == 0))).all()
    session.close()

    if response:
        for msg in response:
            msg = convert_record_to_list(msg)
            bot.send_message(message.chat.id, f'{msg[7]}\n\n{msg[8]}')

            session = Session()
            response2 = session.query(Notification).get(msg[5])
            response2.is_viewed = 1
            session.add(response2)
            session.commit()
            session.close()
    else:
        bot.send_message(message.chat.id, 'У вас нет новых уведомлений')


def search_products(message):
    session = Session()
    user_resource = session.query(User, UserInfo).join(UserInfo).filter(User.telegram_chat_id == message.chat.id).all()
    user_resource = convert_record_to_list(user_resource[0])
    user_resource[0] = user_resource[0][1:]

    response = session.query(Product).filter(and_((Product.category.ilike('%' + message.text + '%')),
                                                  (Product.is_confirmed == 1),
                                                  not_(Product.user_id == user_resource[0]))) \
        .order_by(desc(Product.id)) \
        .limit(3).all()

    session.close()

    if response:
        for item in response:
            item = convert_record_to_list(item)

            keyboard = telebot.types.InlineKeyboardMarkup()

            if user_resource[9] == "поставщик":
                keyboard.row(
                    telebot.types.InlineKeyboardButton('Купить', callback_data='buy-product|' + item[0]),
                    telebot.types.InlineKeyboardButton('Выложить СТЕ', callback_data='create-product|' + item[0])
                )
            else:
                keyboard.row(
                    telebot.types.InlineKeyboardButton('Купить', callback_data='buy-product|' + item[0]),
                )

            bot.send_message(message.chat.id,
                             f'Название: {item[2]}\nКатегория: {item[3]}\nКод КПГЗ: {item[4]}\nЦена за ед.: {item[6]}',
                             reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Нет товаров данной категории', reply_markup=include_main_menu())


def buy_product(message, id):
    session = Session()
    try:
        response = session.query(Product).filter(Product.id == id).all()
        response2 = session.query(User).filter(User.telegram_chat_id == message.chat.id).all()

        response = convert_record_to_list(response[0])
        response2 = convert_record_to_list(response2[0])

        price = str(int(message.text) * int(response[6]))
        prod = Offer(
            product_id=id,
            seller_id=response[1],
            buyer_id=response2[0],
            amount=price,
            quantity=message.text,
            status="заявка"
        )

        notify = Notification(
            user_id=response[1],
            title="Покупка продукта",
            description=f"Продукт: {response[2]}\nКоличество: {message.text}\nНа сумму: {price}",
            is_viewed=0
        )

        session.add(notify)
        session.add(prod)
        session.commit()

        bot.send_message(message.chat.id, 'Заявка на покупку создана', reply_markup=include_main_menu())
    except:
        msg = bot.send_message(message.chat.id, 'Введите количество покупаемого товара')
        bot.register_next_step_handler(msg, buy_product, id)
    finally:
        session.close()


def create_product(message, id):
    session = Session()
    try:
        response = session.query(Product).get(id)
        response2 = session.query(User).filter(User.telegram_chat_id == message.chat.id).all()
        response2 = convert_record_to_list(response2[0])

        message.text = int(message.text)

        prod = Product(
            user_id=response2[0],
            name=response.name,
            category=response.category,
            code=response.code,
            is_confirmed=0,
            specifications=str(message.text)
        )

        session.add(prod)
        session.commit()

        bot.send_message(message.chat.id, 'СТЕ с вашей ценой добавлен', reply_markup=include_main_menu())
    except:
        msg = bot.send_message(message.chat.id, 'Введите вашу цену за еденицу товара')
        bot.register_next_step_handler(msg, create_product, id)
    finally:
        session.close()


bot.polling(none_stop=True)
