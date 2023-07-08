from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def generate_product_detail(product_id, category_id, quantity):
    markup = InlineKeyboardMarkup()
    minus = InlineKeyboardButton(text='➖', callback_data='minus')
    quan = InlineKeyboardButton(text=str(quantity), callback_data='quantity')
    plus = InlineKeyboardButton(text='➕', callback_data='plus')
    order = InlineKeyboardButton(text='Заказать 😍', callback_data=f'order_{product_id}_{quantity}')
    cart = InlineKeyboardButton(text='Моя корзина 🛒', callback_data=f'show_cart')
    back = InlineKeyboardButton(text='Назад ⏮', callback_data=f'back_{category_id}')
    markup.add(minus, quan, plus)
    markup.add(order, cart)
    markup.add(back)
    return markup


def change_user_data():
    markup = InlineKeyboardMarkup()
    yes = InlineKeyboardButton(text='Да', callback_data='yes-change')
    no = InlineKeyboardButton(text='Нет', callback_data='no-change')
    markup.add(yes, no)
    return markup


def generate_cart_buttons(cart_products, cart_id):
    markup = InlineKeyboardMarkup()

    for cart_product_id, product_name, quantity, final_price in cart_products:
        btn = InlineKeyboardButton(text=product_name, callback_data='product_name')
        minus = InlineKeyboardButton(text='➖', callback_data=f'delete_{cart_product_id}_{quantity}')
        quan = InlineKeyboardButton(text=str(quantity), callback_data='quantity')
        plus = InlineKeyboardButton(text='➕', callback_data=f'add_{cart_product_id}_{quantity}')
        markup.add(btn)
        markup.row(minus, quan, plus)

    if len(cart_products) > 0:
        clear = InlineKeyboardButton(text='Очистить', callback_data=f'clear_{cart_id}')
        order = InlineKeyboardButton(text='Оформить заказ', callback_data=f'buy_{cart_id}')
        markup.row(clear, order)
    main = InlineKeyboardButton(text='На главную', callback_data='main_menu')
    markup.row(main)
    return markup


