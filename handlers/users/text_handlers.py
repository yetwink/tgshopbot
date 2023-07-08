from data.loader import bot, dp, db
from aiogram.types import Message, LabeledPrice, ShippingOption, Update, ReplyKeyboardRemove
from data.configs import NUMBERS
from aiogram.dispatcher import FSMContext
from states.states import Form, Feedback
import random
import re
from keyboards.reply import generate_main_menu, generate_categories, settings_change_name_phone
from keyboards.inline import generate_product_detail, change_user_data


async def start_register(message: Message):
    chat_id = message.chat.id
    text = 'Введите ваше имя и фамилию'
    # Сейчас будет вопрос
    await Form.full_name.set()
    await bot.send_message(chat_id, text)


@dp.message_handler(state=Form.full_name, regexp=r'[А-Яа-яA-Za-z]+ [А-Яа-яA-Za-z]+')  # Сигнал что функция будет ждать ответ
async def get_full_name_ask_phone(message: Message, state: FSMContext):
    # Открыть оперативку и сохранить данные
    async with state.proxy() as data:
        data['full_name'] = message.text
    # await Form.phone.set()
    await Form.next()
    await bot.send_message(message.chat.id, 'Введите свой номер телефона\nВ формате +998901234567')


@dp.message_handler(state=Form.full_name)
async def get_error_name(message: Message, state: FSMContext):
    await bot.send_message(message.chat.id, 'Не верный формат имени. Попробуйте снова')


@dp.message_handler(state=Form.phone)
async def get_phone_ask_key(message: Message, state: FSMContext):
    chat_id = message.chat.id
    if re.search(r'^\+998\d{9}$', message.text):
        text = ' '.join([random.choice(list(NUMBERS)) for i in range(4)])
        answer = ''.join([str(NUMBERS[key]) for key in text.split(' ')])
        async with state.proxy() as data:
            data['phone'] = message.text
            data['answer'] = answer
        message_to_user = f'Введите код из сообщения в формате: {answer}\n\n{text}'
        await Form.next()
        await bot.send_message(chat_id, message_to_user)
    else:
        await bot.send_message(chat_id, 'Не верный формат телефона. Попробуйте снова')


@dp.message_handler(state=Form.key)
async def get_key_ask_finish_register(message: Message, state: FSMContext):
    chat_id = message.chat.id
    user_exists = db.get_user_by_id(chat_id)
    async with state.proxy() as data:
        answer = data['answer']
        if message.text == answer:
            full_name = data['full_name']
            phone = data['phone']
            if user_exists:
                db.update_user_fullname_phone(chat_id, full_name, phone)
                await bot.send_message(chat_id, 'Ваши данные успешно обновлены!')
            else:
                db.save_user(chat_id, full_name, phone)
                await bot.send_message(chat_id, 'Регистрация прошла успешно')
            await state.finish()
            await show_main_menu(message)
        else:
            await bot.send_message(chat_id, 'Не верный код. Попробуйте снова')


@dp.message_handler(regexp='Главное меню')
async def show_main_menu(message: Message):
    chat_id = message.chat.id
    message_id = message.message_id
    await bot.delete_message(chat_id, message_id)
    try:
        await bot.delete_message(chat_id, message_id - 1)
    except:
        pass
    await bot.send_message(chat_id, 'Выберите одно из следующих',
                           reply_markup=generate_main_menu())


@dp.message_handler(regexp='(🍴 Меню|Назад к категориям)')
async def show_categories(message: Message):
    chat_id = message.chat.id
    message_id = message.message_id
    await bot.delete_message(chat_id, message_id)
    try:
        await bot.delete_message(chat_id, message_id - 1)
    except:
        pass
    categories = db.get_categories()
    await bot.send_message(chat_id, 'Выберите категорию',
                     reply_markup=generate_categories(categories, 'categories'))


categories = [i[0] for i in db.get_categories()] # [(''), ('')] -> ['', '']


@dp.message_handler(lambda message: message.text in categories)
async def show_products(message: Message):
    chat_id = message.chat.id

    category_name = message.text
    message_id = message.message_id
    await bot.delete_message(chat_id, message_id)
    await bot.delete_message(chat_id, message_id - 1)
    category_id, image = db.get_category_detail(category_name)
    products = db.get_products_names(category_id)
    with open(image, mode='rb') as img:
        await bot.send_photo(chat_id, img, reply_markup=generate_categories(products, 'products'))

products = [i[0] for i in db.get_all_products_names()]  # [(), ()] -> ['', '']


@dp.message_handler(lambda message: message.text in products)
async def product_detail(message: Message):
    chat_id = message.chat.id
    product_name = message.text
    # Надо взять всю информацию о товаре
    product = db.get_product_detail(product_name)
    message_id = message.message_id
    await bot.delete_message(chat_id, message_id)
    await bot.delete_message(chat_id, message_id - 1)
    with open(product[4], mode='rb') as img:
        text = f'''{product[1]}

<b>Описание:</b> {product[3]}

<b>Цена:</b> {product[2]} сум'''
        await bot.send_photo(chat_id, img, caption=text, reply_markup=generate_product_detail(product[0], product[-1], 1))


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


@dp.message_handler(regexp='Корзина 🛒')
async def show_cart_text(message: Message):
    try:
        chat_id = message.chat.id
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

        text += f'''Общее количество: {0 if total_products is None else total_products}\n\n
Общая стоимость: {0 if total_price is None else total_price}'''

        await bot.send_invoice(chat_id=chat_id,
                               title='Лучший тг-бот магазин',
                               description=text,
                               payload='bot-defined invoice payload',
                               provider_token='TOKEN',
                               currency='UZS',
                               need_name=True,
                               is_flexible=True,
                               prices=[
                                   LabeledPrice(
                                       label=f'{data[1]} - {data[2]}',
                                       amount=int(data[3] * 100)
                                   ) for data in cart_products
                               ])
    except:
        textt = 'Ваша корзина пуста. Перейдите в меню и добавьте товаров в корзину'
        await bot.send_message(message.chat.id, textt, reply_markup=generate_main_menu())


@dp.message_handler(regexp='🛍 Мои заказы')
async def my_orders(message: Message):
    chat_id = message.chat.id
    try:
        cart_id = db.get_cart_id(chat_id)
    except:
        db.create_cart_for_user(chat_id)
        cart_id = db.get_cart_id(chat_id)

    all_user_orders = db.get_all_orders(cart_id)
    order_prices = [i[2] for i in all_user_orders]
    all_order_id = [i[0] for i in all_user_orders]

    text = f'<b>Ваши последние заказы:</b>\n\n'

    for order_id in all_order_id:
        order = db.get_all_order_products(order_id)

        text += f'''Номер заказа: {order_id}\n\n'''
        i = 0
        price = f'<b>Общая стоимость:</b> {order_prices[i]}\n\n'

        for product in order:

            i += 1
            text += f'''{i}. {product[2]}
Количество: {product[3]}
Стоимость: {product[4]}\n
'''
        text += price

    await bot.send_message(chat_id, text, reply_markup=generate_main_menu())


@dp.message_handler(regexp='✍ Оставить отзыв')
async def user_feedback(message: Message):

    chat_id = message.chat.id
    userfullname = message.from_user.full_name
    textt = f'{userfullname}, здесь вы можете оставить свой отзыв!\n\n<b>Напишите что-нибудь:</b>'
    await Feedback.otziv.set()
    await bot.send_message(chat_id, textt, reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=Feedback.otziv, content_types=['sticker', 'photo', 'voice', 'text', 'gif'])
async def get_feedback(message: Message, state: FSMContext):

    manager_id = -862926535  # id группы/чата куда придет отзыв
    if message.text:
        await bot.send_message(manager_id, f'Пользователь <b>{message.from_user.full_name}</b> оставил отзыв!\n\n"{message.text}"')
        await state.finish()
        await bot.send_message(message.chat.id, 'Сообщение отправлено. Спасибо за ваш отзыв!', reply_markup=generate_main_menu())
    else:
        await bot.send_message(message.chat.id, 'Неверный формат отзыва. Напишите снова')


@dp.message_handler(regexp='⚙ Настройки')
async def settings(message: Message):
    chat_id = message.chat.id
    text = 'Выберите действие:'
    await bot.send_message(chat_id, text, reply_markup=settings_change_name_phone())


@dp.message_handler(regexp='👤Изменить имя и номер телефона')
async def change_name_phone(message: Message):
    chat_id = message.chat.id
    full_name, phone = db.get_user_fullname_phone(chat_id)
    text = f'''Хотите изменить ваши данные?\n
Ваше имя: {full_name}
Ваш номер телефона: {phone}\n
Выберите дейсвтие:
'''
    await bot.send_message(chat_id, text, reply_markup=change_user_data())





