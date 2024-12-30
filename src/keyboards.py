from enum import Enum
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class Callbacks(Enum):
    EMPTY = "empty"
    CLOSE = "close"

def link_markup(title: str, user_id: int) -> InlineKeyboardMarkup:
    """
    Создает встроенную клавиатуру с кнопками.

    :param title: Текст для первой кнопки.
    :param user_id: ID пользователя для ссылки.
    :return: Экземпляр InlineKeyboardMarkup с кнопками.
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=title, callback_data=Callbacks.EMPTY.value)],
        [InlineKeyboardButton(text="👤", url=f"tg://user?id={user_id}")],
        [InlineKeyboardButton(text="❌", callback_data=Callbacks.CLOSE.value)]
    ])