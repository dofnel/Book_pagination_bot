BOOK_PATH = '../bookBot_pagination/book/Bredberi_Marsianskie-hroniki.txt'


# Функция, которая правильно обрезает текст до последнего знака препинания
def get_part_text(text, start, page_size):
    sym = [',', '.', '!', ':', ';', '?']
    test = page_size + start - 1

    if len(text[start:]) < page_size:
        return text[start:], len(text[start:])

    while text[test] not in sym or (text[test+1] in sym or text[test-1] in sym):
        test -= 1

    return text[start:test+1], len(text[start:test+1])


PAGE_SIZE = 1050
book: dict[int, str] = {}


# Функция, добавляющая правильно обрезанный текст в dict определенного пользователя
def prepare_book(path: str):
    with open(path, 'r', encoding='utf8') as file:
        text = file.read().lstrip()

    page, start = 1, 0

    while start < len(text):
        str_text, length = get_part_text(text, start, PAGE_SIZE)
        book[page] = str_text.lstrip()
        page += 1
        start += length


prepare_book(BOOK_PATH)
