from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def generate_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    make_order = KeyboardButton('🍴 Меню')
    cart = KeyboardButton('Корзина 🛒')
    my_orders = KeyboardButton('🛍 Мои заказы')
    feedback = KeyboardButton('✍ Оставить отзыв')
    settings = KeyboardButton('⚙ Настройки')
    markup.add(make_order)
    markup.add(my_orders, cart)
    markup.add(feedback, settings)
    return markup


def generate_categories(categories, item):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = []
    for category in categories:
        btn = KeyboardButton(text=category[0]) # [('Сеты'), ()]
        buttons.append(btn)
    markup.add(*buttons)
    if item == 'categories':
        btn = KeyboardButton('Главное меню')
    elif item == 'products':
        btn = KeyboardButton('Назад к категориям')
    markup.row(btn)

    return markup


def settings_change_name_phone():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    change_name_phone = KeyboardButton('👤Изменить имя и номер телефона')
    back = KeyboardButton('Главное меню')
    markup.add(change_name_phone)
    markup.add(back)
    return markup


