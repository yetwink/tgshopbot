from data.loader import bot, dp, executor
import handlers

if __name__ == '__main__':
    executor.start_polling(dp)