from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from lexicon.lexicon import LEXICON


def create_paginator(indi: int, bm=None) -> InlineKeyboardBuilder:
    number = bm

    if bm is not None:
        number = bm

    callback_buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=LEXICON['backward'], callback_data='backward'),
        InlineKeyboardButton(text=f"{number}/{LEXICON['book_len']}", callback_data='bookmarks'),
        InlineKeyboardButton(text=LEXICON['forward'], callback_data='forward')
    ]

    # Инициализируем Inline Builder
    callback_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    callback_builder.row(*callback_buttons)

    return callback_builder
