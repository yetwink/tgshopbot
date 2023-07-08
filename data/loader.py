from aiogram import Bot, Dispatcher, executor
from data.configs import TOKEN
from database.database import DataBase
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()

bot = Bot(TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, storage=storage)
db = DataBase()


