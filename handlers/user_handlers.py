from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from lexicon.lexicon import LEXICON
from database.database import users_db
from services.file_handling import book
from keyboards.paginator_kb import create_paginator
from keyboards.bookmarks_buttons import create_bookmarks_buttons, delete_bookmarks
from filters.bookmarks_filter import IsBookmarkCallback, IsDeleteBookmarks

router: Router = Router()


@router.message(F.text == '/start')
async def start_process(message: Message):
    await message.answer(text=LEXICON['/start'])

    if message.from_user.id not in users_db:
        users_db[message.from_user.id] = {'page': 1,
                                          'bookmarks': set()}

        print(users_db)


@router.message(F.text == '/help')
async def help_process(message: Message):
    await message.answer(text=LEXICON['/help'])


@router.message(F.text == '/beginning')
async def bookmarks_process(message: Message):
    id = message.from_user.id

    await message.answer(text=book[1],
                         reply_markup=create_paginator(id, 1).as_markup(resize_keyboard=True))


@router.message(F.text == '/continue')
async def continue_process(message: Message):
    id = message.from_user.id
    await message.answer(text=book[users_db[id]['page']],
                         reply_markup=create_paginator(id).as_markup(resize_keyboard=True))


@router.callback_query(F.data == 'backward')
async def backward_callback_button(callback: CallbackQuery):
    id = callback.from_user.id

    if users_db[id]['page'] >= 2:
        users_db[id]['page'] -= 1

        await callback.message.edit_text(text=book[users_db[id]['page']],
                                         reply_markup=create_paginator(id).as_markup(resize_keyboard=True))
    else:
        await callback.answer(text='Вы находитесь на первой странице',
                              show_alert=True)


@router.callback_query(F.data == 'forward')
async def forward_callback_button(callback: CallbackQuery):
    id = callback.from_user.id

    if users_db[id]['page'] < list(book.keys())[-1]:
        users_db[id]['page'] += 1

        await callback.message.edit_text(text=book[users_db[id]['page']],
                                         reply_markup=create_paginator(id).as_markup(resize_keyboard=True))
    else:
        await callback.answer(text='Вы на последней странице',
                              show_alert=True)


@router.callback_query(F.data == 'bookmarks')
async def bookmarks_callback_button(callback: CallbackQuery):
    id = callback.from_user.id
    page = users_db[id]['page']

    if page not in users_db[id]['bookmarks']:
        users_db[id]['bookmarks'].add(page)
        await callback.answer(text=f'Страница {page} добавлена в закладки')
        print(users_db[id]['bookmarks'])
    else:
        await callback.answer(text='Страница уже в закладках',
                              show_alert=True)


@router.message(F.text == '/bookmarks')
async def bookmarks_button(message: Message):
    id = message.from_user.id
    await message.answer(text=LEXICON['/bookmarks'],
                         reply_markup=create_bookmarks_buttons(id).as_markup(resize_keyboard=True))


@router.callback_query(F.data == 'cancel')
async def cancel_callback(callback: CallbackQuery):
    id = callback.from_user.id
    page = users_db[id]['page']

    await callback.message.edit_text(text=book[page],
                                     reply_markup=create_paginator(id).as_markup())


@router.callback_query(F.data == 'cancel_del')
async def cancel_del_callback(callback: CallbackQuery):
    id = callback.from_user.id

    await callback.message.edit_text(text=f"{LEXICON['/bookmarks']}",
                                     reply_markup=create_bookmarks_buttons(id).as_markup(resize_keyboard=True))


@router.callback_query(IsBookmarkCallback())
async def return_from_bookmarks(callback: CallbackQuery):
    id = callback.from_user.id
    bm_page = int(callback.data[10:])

    await callback.message.edit_text(text=book[bm_page],
                                     reply_markup=create_paginator(id, bm_page).as_markup(resize_keyboard=True))


@router.callback_query(F.data == 'edit_bookmarks_button')
async def delete_from_bookmarks_buttons(callback: CallbackQuery):
    id = callback.from_user.id

    await callback.message.edit_text(text='Редактирование закладок',
                                     reply_markup=delete_bookmarks(id).as_markup(resize_keyboard=True))


@router.callback_query(IsDeleteBookmarks())
async def delete_from_bookmarks(callback: CallbackQuery):
    id = callback.from_user.id
    number = int(callback.data[4:])
    page = users_db[id]['page']

    buttons_del: set = users_db[id]['bookmarks']
    buttons_del.discard(number)

    if len(buttons_del) >= 1:
        await callback.message.edit_text(text='Редактирование закладок',
                                         reply_markup=delete_bookmarks(id).as_markup(resize_keyboard=True))
    else:
        await callback.answer(text='Список закладок пуст')
        await callback.message.edit_text(text=book[page],
                                         reply_markup=create_paginator(id).as_markup())


@router.message()
async def any_other_message(message: Message):
    await message.answer(LEXICON['wrong_message'])
