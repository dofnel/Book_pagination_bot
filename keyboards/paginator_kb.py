from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from database.database import users_db
from lexicon.lexicon import LEXICON


def create_paginator(indi: int, bm=None) -> InlineKeyboardBuilder:
    number = bm

    if bm is None:
        number = users_db[indi]['page']

    callback_buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=LEXICON['backward'], callback_data='backward'),
        InlineKeyboardButton(text=f"{number}/{LEXICON['book_len']}", callback_data='bookmarks'),
        InlineKeyboardButton(text=LEXICON['forward'], callback_data='forward')
    ]

    # Инициализируем Inline Builder
    callback_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    callback_builder.row(*callback_buttons)

    return callback_builder
