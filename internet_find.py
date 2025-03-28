import webbrowser
from urllib.parse import quote
from forbidden import forbidden_func

# webbrowser для открытия ссылок, quote для кодирования самого url

def web_search(command):
    # Поиск в инете.
    try:
        # Проверяем начинается ли команда с "поиск " и содержит кавычки
        if command.lower().startswith('поиск "') and command.count('"') >= 2:
            # Извлекаем текст между первыми кавычками
            query = command.split('"')[1]

            forbidden = forbidden_func() # Подгружаем запрещенные словечки
            string_forbidden = "" # Для формирования запрещенной строки

            # Многословный запрос
            if len(query.split()) > 1:
                for resp in query.split():
                    if resp in forbidden:
                        string_forbidden += resp + " "

            elif query in forbidden:
                raise ValueError(f"Ты че... Я был о тебе лучшего мнения, чел... \nКакие {query}? Ты серьезно?!")

            # формируем запретную строку
            if string_forbidden != "": raise ValueError(f"Ты че... Я был о тебе лучшего мнения, чел... \nКакие {string_forbidden}? Ты серьезно?!")

            webbrowser.open(f"https://www.google.com/search?q={quote(query)}")
            return f"Открываю результаты для: {query}"

        return "Неверный формат. Используйте: поиск \"запрос\""
    except Exception as e:
        return f"Ошибка поиска: {str(e)}"