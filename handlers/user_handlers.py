from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from lexicon.lexicon import LEXICON
from database.database import users_db
from keyboards.paginator_kb import create_paginator
from keyboards.bookmarks_buttons import create_bookmarks_buttons, delete_bookmarks
from filters.bookmarks_filter import IsBookmarkCallback, IsDeleteBookmarks
from services.reach_photo import get_photo

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

    photo = get_photo(1)

    await message.answer_photo(photo=photo,
                               reply_markup=create_paginator(id, 1).as_markup(resize_keyboard=True))


@router.message(F.text == '/continue')
async def continue_process(message: Message):
    id = message.from_user.id
    page = users_db[id]['page']
    photo = get_photo(page)

    await message.answer_photo(photo,
                               reply_markup=create_paginator(id).as_markup(resize_keyboard=True))


# Редактор InlineButton (<<), которая используется в paginator
@router.callback_query(F.data == 'backward')
async def backward_callback_button(callback: CallbackQuery):
    id = callback.from_user.id

    if users_db[id]['page'] >= 2:
        users_db[id]['page'] -= 1

        page = users_db[id]['page']
        photo = get_photo(page)

        await callback.message.edit_media(media=InputMediaPhoto(media=photo),
                                          reply_markup=create_paginator(id).as_markup(
                                             resize_keyboard=True))
    else:
        await callback.answer(text='Вы находитесь на первой странице',
                              show_alert=True)


# Inline button, переходящая на следующую страницу (>>)
@router.callback_query(F.data == 'forward')
async def forward_callback_button(callback: CallbackQuery):
    id = callback.from_user.id

    if users_db[id]['page'] < LEXICON['book_len']:
        users_db[id]['page'] += 1

        page = users_db[id]['page']
        photo = get_photo(page)

        await callback.message.edit_media(media=InputMediaPhoto(media=photo),
                                          reply_markup=create_paginator(id).as_markup(
                                             resize_keyboard=True))
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
    else:
        await callback.answer(text='Страница уже в закладках',
                              show_alert=True)


@router.message(F.text == '/bookmarks')
async def bookmarks_button(message: Message):
    id = message.from_user.id
    await message.answer(text=LEXICON['/bookmarks'],
                         reply_markup=create_bookmarks_buttons(id).as_markup(resize_keyboard=True))


# Кнопка отмены в закладках
@router.callback_query(F.data == 'cancel')
async def cancel_callback(callback: CallbackQuery):
    id = callback.from_user.id
    page = users_db[id]['page']
    photo = get_photo(page)

    await callback.message.delete()
    await callback.message.answer_photo(photo=photo,
                                        reply_markup=create_paginator(id).as_markup())


# Кнопка отмены в редактировании закладов
@router.callback_query(F.data == 'cancel_del')
async def cancel_del_callback(callback: CallbackQuery):
    id = callback.from_user.id

    await callback.message.edit_text(text=f"{LEXICON['/bookmarks']}",
                                     reply_markup=create_bookmarks_buttons(id).as_markup(resize_keyboard=True))


# Вывод страницы после нажатия на нее в закладках (callback data начинается с bookmarks_)
@router.callback_query(IsBookmarkCallback())
async def return_from_bookmarks(callback: CallbackQuery):
    id = callback.from_user.id
    bm_page = int(callback.data[10:])
    photo = get_photo(bm_page)

    await callback.message.delete()
    await callback.message.answer_photo(photo=photo,
                                        reply_markup=create_paginator(id, bm_page).as_markup(resize_keyboard=True))


# Сообщение, в котором можно удалить страницы из закладок, со списком закладок и кнопкой отмены
@router.callback_query(F.data == 'edit_bookmarks_button')
async def delete_from_bookmarks_buttons(callback: CallbackQuery):
    id = callback.from_user.id

    await callback.message.edit_text(text='Редактирование закладок',
                                     reply_markup=delete_bookmarks(id).as_markup(resize_keyboard=True))


# callback data при удалении кнопки из закладок
@router.callback_query(IsDeleteBookmarks())
async def delete_from_bookmarks(callback: CallbackQuery):
    id = callback.from_user.id
    number = int(callback.data[4:])
    photo = get_photo(number)

    buttons_del: set = users_db[id]['bookmarks']
    buttons_del.discard(number)

    if len(buttons_del) >= 1:
        await callback.message.edit_text(text='Редактирование закладок',
                                         reply_markup=delete_bookmarks(id).as_markup(resize_keyboard=True))
    else:
        await callback.answer(text='Список закладок пуст')
        await callback.message.delete()
        await callback.message.answer_photo(photo=photo,
                                            reply_markup=create_paginator(id).as_markup())


# Выводит страницу по номеру введенного числа
@router.message(lambda x: x.text and x.text.isdigit() and 121 > int(x.text) > 0)
async def number_of_page(message: Message):
    id = message.from_user.id

    if int(message.text) > users_db[id]['page']:
        users_db[id]['page'] = int(message.text)

    photo = get_photo(int(message.text))

    await message.answer_photo(photo, reply_markup=create_paginator(id, int(message.text)).as_markup())


@router.message(F.from_user.id == 6008286293)
async def test(message: Message):
    await message.answer(str(users_db))


@router.message()
async def any_other_message(message: Message):
    await message.answer(LEXICON['wrong_message'])
