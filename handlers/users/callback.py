from aiogram.types import CallbackQuery, LabeledPrice, ShippingOption
from data.loader import bot, db, dp
from keyboards.inline import generate_product_detail, generate_cart_buttons
from keyboards.reply import generate_categories, generate_main_menu
from .text_handlers import start_register


@dp.callback_query_handler(lambda call: call.data == 'plus')
async def reaction_to_plus(call: CallbackQuery):
    chat_id = call.message.chat.id
    buttons = call.message.reply_markup.inline_keyboard
    quantity = int(buttons[0][1].text)
    product_id = buttons[1][0].callback_data.split('_')[1]
    # order_1_1 -> ['order', '1', '1']
    category_id = buttons[2][0].callback_data.split('_')[1]
    if quantity < 20:
        quantity += 1
        await bot.edit_message_reply_markup(chat_id, call.message.message_id,
            reply_markup=generate_product_detail(product_id, category_id, quantity))
    else:
        await bot.answer_callback_query(call.id, 'Вы не можете купить больше 20 товаров')


@dp.callback_query_handler(lambda call: call.data == 'minus')
async def reaction_to_minus(call: CallbackQuery):
    chat_id = call.message.chat.id
    buttons = call.message.reply_markup.inline_keyboard
    quantity = int(buttons[0][1].text)
    product_id = buttons[1][0].callback_data.split('_')[1]
    # order_1_1 -> ['order', '1', '1']
    category_id = buttons[2][0].callback_data.split('_')[1]
    if quantity > 1:
        quantity -= 1
        await bot.edit_message_reply_markup(chat_id, call.message.message_id,
            reply_markup=generate_product_detail(product_id, category_id, quantity))
    else:
        await bot.answer_callback_query(call.id, 'Вы не можете купить менее 1 товара')


@dp.callback_query_handler(lambda call: call.data == 'quantity')
async def reaction_to_quantity(call: CallbackQuery):
    # Взять quantity и сделать ОТВЕТ "Вы выбрали {quantity} шт"
    chat_id = call.message.chat.id
    buttons = call.message.reply_markup.inline_keyboard
    quantity = int(buttons[0][1].text)
    await bot.answer_callback_query(call.id, f'Вы выбрали {quantity} шт.')


@dp.callback_query_handler(lambda call: 'back' in call.data)
async def back_products_list(call: CallbackQuery):
    chat_id = call.message.chat.id
    category_id = call.data.split('_')[1]
    message_id = call.message.message_id
    await bot.delete_message(chat_id, message_id)
    category = db.get_category_by_id(category_id)
    category_name = category[1]
    image = category[2]
    products = db.get_products_names(category_id)
    with open(image, mode='rb') as img:
        await bot.send_photo(chat_id, img, reply_markup=generate_categories(products, 'products'))


@dp.callback_query_handler(lambda call: 'order' in call.data)
async def add_product_to_cart(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, product_id, quantity = call.data.split('_') # ['order', '1', '5']
    product_id, quantity = int(product_id), int(quantity)
    # Вытащить id корзины. Но так как у нас его нет, еще создать корзину
    try:
        cart_id = db.get_cart_id(chat_id)
    except:
        db.create_cart_for_user(chat_id)
        cart_id = db.get_cart_id(chat_id)
    # Вытащить название и цену товара
    product_name, price = db.get_product_name_price(product_id)
    final_price = price * quantity
    # Добавления товара или изменение товара в корзине
    try:
        db.insert_cart_product(cart_id, product_name, quantity, final_price)
        await bot.answer_callback_query(call.id, 'Продукт успешно добавлен в корзину')
    except:
        db.update_cart_product(cart_id, product_name, quantity, final_price)
        await bot.answer_callback_query(call.id, f'Количество изменено на {quantity}')


@dp.callback_query_handler(lambda call: call.data == 'main_menu')
async def main_menu_call(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    await bot.delete_message(chat_id, message_id)
    try:
        await bot.delete_message(chat_id, message_id - 1)
    except:
        pass
    await bot.send_message(chat_id, 'Выберите одно из следующих',
                           reply_markup=generate_main_menu())


@dp.callback_query_handler(lambda call: call.data == 'show_cart')
async def show_cart(call: CallbackQuery):
    chat_id = call.message.chat.id
    cart_id = db.get_cart_id(chat_id)
    # Обновить общую цену и общее количество товаров в корзине
    db.update_total_price_quantity(cart_id)
    # Вытащить общую цену и общее количество
    total_products, total_price = db.get_total_price_quantity(cart_id)
    # Вытащить товары из корзины
    cart_products = db.get_cart_products(cart_id)  # [(1,2,3), ()]
    # Показать товары в корзине
    text = 'Ваша корзина: \n\n'
    i = 0
    for cart_product_id, product_name, quantity, final_price in cart_products:
        i += 1
        text += f'''{i}. {product_name}
Количество: {quantity}
Общая стоимость: {final_price}\n\n'''

    text += f'''Общее количество: {0 if total_products is None else total_products}
Общая стоимость: {0 if total_price is None else total_price}'''

    await bot.send_message(chat_id, text, reply_markup=generate_cart_buttons(cart_products, cart_id))


@dp.callback_query_handler(lambda call: 'add' in call.data)
async def add_to_cart(call: CallbackQuery):
    chat_id = call.message.chat.id
    cart_product_id = int(call.data.split('_')[1])
    quantity = int(call.data.split('_')[2])
    if quantity + 1 <= 20:
        db.add_quantity_to_cart(cart_product_id, quantity+1)
        await bot.delete_message(chat_id, call.message.message_id)
        await show_cart(call)
    else:
        await bot.answer_callback_query(call.id, 'Нельзя купить более 20 товаров 1 наименования')


@dp.callback_query_handler(lambda call: 'delete' in call.data)
async def delete_to_cart(call: CallbackQuery):
    chat_id = call.message.chat.id
    cart_product_id = int(call.data.split('_')[1])
    quantity = int(call.data.split('_')[2])

    if quantity - 1 == 0:
        db.delete_cart_product(cart_product_id)
        await bot.delete_message(chat_id, call.message.message_id)
        await show_cart(call)
    else:
        db.add_quantity_to_cart(cart_product_id, quantity-1)
        await bot.delete_message(chat_id, call.message.message_id)
        await show_cart(call)


@dp.callback_query_handler(lambda call: 'clear_' in call.data)
async def clear_cart(call: CallbackQuery):
    chat_id = call.message.chat.id
    cart_id = int(call.data.split('_')[1])
    db.delete_cart_products(cart_id)
    await bot.delete_message(chat_id, call.message.message_id)
    await show_cart(call)

EXPRESS_SHIPPING = ShippingOption(
    id='post_express',
    title='До 3х часов',
    prices=[LabeledPrice('До 3х часов', 25_000_00)]
)

REGULAR_SHIPPING = ShippingOption(
    id='post_regular',
    title='Самовывоз',
    prices=[LabeledPrice('Самовывоз', 0)]
)

REGION_SHIPPING = ShippingOption(
    id='post_region',
    title='Доставка в регионы',
    prices=[LabeledPrice('Доставка в регионы', 250_000_00)]
)


@dp.callback_query_handler(lambda call: 'buy' in call.data)
async def create_order(call: CallbackQuery):
    chat_id = call.message.chat.id
    cart_id = int(call.data.split('_')[1])
    total_products, total_price = db.get_total_price_quantity(cart_id)
    # Вытащить товары из корзины
    cart_products = db.get_cart_products(cart_id)  # [(1,2,3), ()]
    # Показать товары в корзине
    text = 'Ваш заказ: \n\n'
    i = 0
    for cart_product_id, product_name, quantity, final_price in cart_products:
        i += 1
        text += f'''{i}. {product_name}
Количество: {quantity}
Общая стоимость: {final_price}\n\n'''

    text += f'''Общее количество: {0 if total_products is None else total_products}
Общая стоимость: {0 if total_price is None else total_price}'''

    await bot.send_invoice(chat_id=chat_id,
                           title='Лучший тг-бот магазин',
                           description=text,
                           payload='bot-defined invoice payload',
                           provider_token='398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065',
                           currency='UZS',
                           need_name=True,
                           is_flexible=True,
                           prices=[
                               LabeledPrice(
                                   label=f'{data[1]} - {data[2]}',
                                   amount=int(data[3] * 100)
                               ) for data in cart_products
                           ])


@dp.shipping_query_handler(lambda query: True)
async def shipping(shipping_query):
    await bot.answer_shipping_query(shipping_query.id,
                              ok=True,
                              shipping_options=[REGULAR_SHIPPING,
                                                REGION_SHIPPING,
                                                EXPRESS_SHIPPING],
                              error_message='Сорри, шото пошло не так..'
                              )


@dp.pre_checkout_query_handler(lambda query: True)
async def checkout(pre_checkout_query):
    await bot.answer_pre_checkout_query(pre_checkout_query.id,
                                        ok=True,
                                        error_message='оп, снова шото не так(')


@dp.message_handler(content_types=['successful_payment'])
async def get_successful_payment(message):
    chat_id = message.chat.id
    cart_id = db.get_cart_id(chat_id)
    admin_id = -862926535
    await bot.send_message(chat_id, 'Товарищ мамонт, оплата успешно проведена! Вас заскамили :)', reply_markup=generate_main_menu())

    full_name, phone = db.get_user_fullname_phone(chat_id)

    total_products, total_price = db.get_total_price_quantity(cart_id)
    cart_products = db.get_cart_products(cart_id)
    db.insert_order(cart_id, total_price, total_products)
    order_id = db.get_order_id(cart_id)[0]

    text = f'''<b>Новый заказ!</b> 
Номер заказа - {order_id}\n
Клиент: <b>{full_name}</b> 
Номер: {phone}\n\n'''
    i = 0
    for cart_product_id, product_name, quantity, final_price in cart_products:
        i += 1
        text += f'''{i}. {product_name}
Количество: {quantity}\n\n'''
        db.insert_order_products(order_id, product_name, quantity, final_price)
    text += f'Общая стоимость заказа: {total_price}'
    db.delete_cart_products(cart_id)
    db.cart_refresh(cart_id)
    await bot.send_message(admin_id, text)


@dp.callback_query_handler(lambda call: call.data == 'no-change')
async def dont_change_user_date(call: CallbackQuery):
    await generate_main_menu()


@dp.callback_query_handler(lambda call: call.data == 'yes-change')
async def change_user_data(call: CallbackQuery):
    await start_register(call.message)


