from data.loader import bot, dp, db
from aiogram.types import Message
from .text_handlers import start_register, show_main_menu


@dp.message_handler(commands=['start'])
async def command_start(message: Message):
    chat_id = message.chat.id
    user = db.get_user_by_id(chat_id)
    if user:
        '''Показать главное меню'''
        await show_main_menu(message)
    else:
        '''Начать регистрацию пользователя'''
        await start_register(message)
