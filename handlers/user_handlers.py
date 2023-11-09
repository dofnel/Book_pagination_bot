from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from lexicon.lexicon import LEXICON
from keyboards.paginator_kb import create_paginator
from keyboards.bookmarks_buttons import create_bookmarks_buttons, delete_bookmarks
from filters.bookmarks_filter import IsBookmarkCallback, IsDeleteBookmarks
from services.reach_photo import get_photo
from database.redis import redis

router: Router = Router()


@router.message(F.text == '/start')
async def start_process(message: Message):
    id = str(message.from_user.id)
    await message.answer(text=LEXICON['/start'])
    # Получаем словарь из redis (user_id:номер страницы)
    page_redis = await redis.hgetall('page')

    if id not in page_redis:
        await redis.hset(name='page', key=id, value=1)


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
    page = await redis.hget('page', str(id))
    photo = get_photo(page)

    await message.answer_photo(photo,
                               reply_markup=create_paginator(id, page).as_markup(resize_keyboard=True))


# Редактор InlineButton (<<), которая используется в paginator
@router.callback_query(F.data == 'backward')
async def backward_callback_button(callback: CallbackQuery):
    id = callback.from_user.id
    page = await redis.hget(name='page', key=id)

    if page >= 2:
        await redis.hset(name='page', key=id, value=page-1)

        page = page - 1
        photo = get_photo(page)

        await callback.message.edit_media(media=InputMediaPhoto(media=photo),
                                          reply_markup=create_paginator(id, page).as_markup(
                                             resize_keyboard=True))
    else:
        await callback.answer(text='Вы находитесь на первой странице',
                              show_alert=True)


# Inline button, переходящая на следующую страницу (>>)
@router.callback_query(F.data == 'forward')
async def forward_callback_button(callback: CallbackQuery):
    id = callback.from_user.id
    page = await redis.hget(name='page', key=id)

    if page < LEXICON['book_len']:
        await redis.hset(name='page', key=id, value=page + 1)

        page = await redis.hget(name='page', key=id)
        photo = get_photo(page)

        await callback.message.edit_media(media=InputMediaPhoto(media=photo),
                                          reply_markup=create_paginator(id, page).as_markup(
                                             resize_keyboard=True))
    else:
        await callback.answer(text='Вы на последней странице',
                              show_alert=True)


# Добавление в закладки при нажатии на центральную кнопку номера страницы в paginator
@router.callback_query(F.data == 'bookmarks')
async def bookmarks_callback_button(callback: CallbackQuery):
    id = callback.from_user.id
    page = await redis.hget(name='page', key=id)
    bm_list = await redis.lrange(id, 0, -1)

    if str(page) not in bm_list:
        await redis.rpush(id, page)
        await callback.answer(text=f'Страница {page} добавлена в закладки')
    else:
        await callback.answer(text='Страница уже в закладках',
                              show_alert=True)


# Команда bookmarks
@router.message(F.text == '/bookmarks')
async def bookmarks_button(message: Message):
    id = message.from_user.id
    bm_list = await redis.lrange(id, 0, -1)
    await message.answer(text=LEXICON['/bookmarks'],
                         reply_markup=create_bookmarks_buttons(id, bm_list).as_markup(resize_keyboard=True))


# Кнопка отмены в закладках
@router.callback_query(F.data == 'cancel')
async def cancel_callback(callback: CallbackQuery):
    id = callback.from_user.id
    page = await redis.hget(name='page', key=id)
    photo = get_photo(page)

    await callback.message.delete()
    await callback.message.answer_photo(photo=photo,
                                        reply_markup=create_paginator(id, page).as_markup())


# Кнопка отмены в редактировании закладов
@router.callback_query(F.data == 'cancel_del')
async def cancel_del_callback(callback: CallbackQuery):
    id = callback.from_user.id
    bm_list = await redis.lrange(id, 0, -1)

    await callback.message.edit_text(text=f"{LEXICON['/bookmarks']}",
                                     reply_markup=create_bookmarks_buttons(id, bm_list).as_markup(resize_keyboard=True))


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
    bm_list = await redis.lrange(id, 0, -1)

    await callback.message.edit_text(text='Редактирование закладок',
                                     reply_markup=delete_bookmarks(id, bm_list).as_markup(resize_keyboard=True))


# callback data при удалении кнопки из закладок
@router.callback_query(IsDeleteBookmarks())
async def delete_from_bookmarks(callback: CallbackQuery):
    id = callback.from_user.id
    number = int(callback.data[4:])
    photo = get_photo(number)
    page = await redis.hget('page', id)

    # Удаляем номер страницы из списка и достаем из redis обновленный список
    await redis.lrem(id, 1, str(number))
    bm_list = await redis.lrange(id, 0, -1)

    if len(bm_list) >= 1:
        await callback.message.edit_text(text='Редактирование закладок',
                                         reply_markup=delete_bookmarks(id, bm_list).as_markup(resize_keyboard=True))
    else:
        await callback.answer(text='Список закладок пуст')
        await callback.message.delete()
        await callback.message.answer_photo(photo=photo,
                                            reply_markup=create_paginator(id, page).as_markup())


# Выводит страницу по номеру введенного числа
@router.message(lambda x: x.text and x.text.isdigit() and 121 > int(x.text) > 0)
async def number_of_page(message: Message):
    id = message.from_user.id
    page = await redis.hget(name='page', key=id)
    current_page = int(message.text)
    bm_list = await redis.lrange(id, 0, -1)

    if str(page) not in bm_list:
        await redis.rpush(id, page)
    await redis.hset(name='page', key=id, value=current_page)

    photo = get_photo(current_page)

    await message.answer_photo(photo, reply_markup=create_paginator(id, current_page).as_markup())


@router.message(F.from_user.id == LEXICON['id'])
async def test(message: Message):
    pages = await redis.hgetall(name='page')
    await message.answer(str(pages))


@router.message()
async def any_other_message(message: Message):
    await message.answer(LEXICON['wrong_message'])
