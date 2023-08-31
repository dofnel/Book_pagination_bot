from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery


# Фильтр для bookmarks
class IsBookmarkCallback(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.data.startswith('bookmarks_')


class IsDeleteBookmarks(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.data.startswith('del_')
