from aiogram.dispatcher.filters.state import State, StatesGroup


class Form(StatesGroup):
    full_name = State()
    phone = State()
    key = State()


class Feedback(StatesGroup):
    otziv = State()

