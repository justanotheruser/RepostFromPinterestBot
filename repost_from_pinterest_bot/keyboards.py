from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def make_row_keyboard(items) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def make_config_keyboard() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text="Повторить"), KeyboardButton(text="Сброс")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
