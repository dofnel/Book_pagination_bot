from aiogram.types import FSInputFile


def get_photo(num: int):
    path_to = f'../bookBot_pagination/book/images_folder/{num}.jpg'
    photo = FSInputFile(path_to)

    return photo
