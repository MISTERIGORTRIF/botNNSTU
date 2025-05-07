import re
import random
import webbrowser
from urllib.parse import quote
from datetime import datetime
import time
import requests
from dotenv import load_dotenv
import os
from textblob import TextBlob
from translate import Translator
import spacy


def weather():
    try:
        CITY = "Нижний Новгород,RU"
        load_dotenv() # Загрузили данные из env
        API_KEY = os.getenv("OPEN_WEATHER_KEY") # Выбрали ключик

        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric&lang=ru" # Ссылочка на сайтик :3

        if API_KEY is None:
            raise ValueError("АПИ ИНОГДА КОКЕТНИЧАЕТ СО МНОЙ ПО-РУССКИ. 🔑🔑🔑🔑🔑")

        if requests.get(url).status_code != 200:
            raise ValueError("ЭЭЭЭЭЭЭ КУДА ПРЕЩЬ?? НЕ ВИДИШЬ КОД НЕ 200??? 💔💔💔")

        print("Загрузка данных...")
        response = requests.get(url) # Запрос
        data = response.json() # Кушаем

        # ---------------Данные о погоде----------------
        city = data["name"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        weather_desc = data["weather"][0]["description"]
        wind_speed = data["wind"]["speed"]
        # ----------------------------------------------

        time.sleep(2) # Спать... И режим. И меня не волнует что сейчас пол первого дня. Я сплю.

        # ---------------Выводим данные о погоде--------
        return (f"Погода в городе {city}: \n"
                     f"- Температура: {temp}°C (ощущается как {feels_like}°C) \n"
                     f"- Описание: {weather_desc.capitalize()} \n"
                     f"- Влажность: {humidity}% \n"
                     f"- Скорость ветра: {wind_speed} м/с")
        # ----------------------------------------------

    except Exception as e:
        return str(e)


def get_weather(CITY_en):
    try:
        #print(CITY_en)
        if CITY_en is None:
            CITY = "Нижний Новгород,RU"
            print("Бот: Не знаю такого... Держи вот Нижний Новгород.")
        else: CITY = CITY_en+",RU"
        #print(CITY)
        load_dotenv() # Загрузили данные из env
        API_KEY = os.getenv("OPEN_WEATHER_KEY") # Выбрали ключик

        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric&lang=ru" # Ссылочка на сайтик :3

        if API_KEY is None:
            raise ValueError("АПИ ИНОГДА КОКЕТНИЧАЕТ СО МНОЙ ПО-РУССКИ. 🔑🔑🔑🔑🔑")

        if requests.get(url).status_code != 200:
            raise ValueError("ЭЭЭЭЭЭЭ КУДА ПРЕЩЬ?? НЕ ВИДИШЬ КОД НЕ 200??? 💔💔💔")

        print("Загрузка данных...")
        response = requests.get(url) # Запрос
        data = response.json() # Кушаем

        # ---------------Данные о погоде----------------
        city = data["name"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        weather_desc = data["weather"][0]["description"]
        wind_speed = data["wind"]["speed"]
        # ----------------------------------------------

        time.sleep(2) # Спать... И режим. И меня не волнует что сейчас пол первого дня. Я сплю.

        # ---------------Выводим данные о погоде--------
        return (f"Погода в городе {city}: \n"
                     f"- Температура: {temp}°C (ощущается как {feels_like}°C) \n"
                     f"- Описание: {weather_desc.capitalize()} \n"
                     f"- Влажность: {humidity}% \n"
                     f"- Скорость ветра: {wind_speed} м/с")
        # ----------------------------------------------

    except Exception as e:
        return str(e)

# Простейший переводчик
def translate_to_english(text):

    translator = Translator(to_lang="en", from_lang="ru")

    try:
        return translator.translate(text).lower()
    except:
        return text


# Анализируем текст
def analyze_sentiment(text):
    """Анализ тональности текста с переводом на английский"""
    try:
        # Проверка на английские символы
        for char in text:
            if (65 <= ord(char) <= 90) or (97 <= ord(char) <= 122):
                return 0.0, "error"  # Возвращаем нейтральный результат вместо ошибки

        text = translate_to_english(text)
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity

        # Определяем тональность
        if polarity > 0.1:
            sentiment = "позитивный"
        elif polarity < -0.1:
            sentiment = "негативный"
        else:
            sentiment = "нейтральный"

        return polarity, sentiment

    except Exception as e:
        print(f"Ошибка анализа тональности: {str(e)}")
        return 0.0, "нейтральный"  # Возвращаем значения по умолчанию при ошибке

# Возвращает ответ в зависимости от тональности
def get_sentiment_response(polarity, sentiment):
    responses = {
        "error": [
            "По русски пиши пожалуйста.",
        ],
        "позитивный": [
            "Я чувствую позитив! Оценка тональности: {:.2f}",
            "Какой позитивный настрой! Тональность: {:.2f}",
            "Ваш энтузиазм заразителен! Оценка: {:.2f}"
        ],
        "негативный": [
            "Мне жаль, что вам плохо... Оценка тональности: {:.2f}",
            "Похоже, вам грустно. Тональность: {:.2f}",
            "Я здесь, чтобы помочь. Оценка настроения: {:.2f}"
        ],
        "нейтральный": [
            "Понятно. Оценка тональности: {:.2f}",
            "Интересно. Тональность сообщения: {:.2f}",
            "Спасибо за сообщение. Оценка: {:.2f}"
        ]
    }
    return random.choice(responses[sentiment]).format(polarity)

#---------------------ВрЕмЯ-------------------
def timer():
    return datetime.now().strftime("%H:%M:%S")
#-----------------------------------------------

#--------------------Определяем словарь шаблонов и ответов--------------------------
responses = {
    # Приветствия
    r"(привет|здравствуй|хай|здаров)": [
        "Привет-привет! Как дела?",
        "Здравствуй! Рад тебя видеть!",
        "Приветствую! Чем могу помочь?",
        "Хай! Как сам?",
        "О, привет! Чего желаешь?"
    ],

    # Как дела
    r"(как дела|как ты|как жизнь|как сам)": [
        "Отлично! А у тебя?",
        "Как в сказке! Только вот дракона нет...",
        "Лучше всех! Ну почти :)",
        "Работаю, не покладая процессора!",
        "Как у бота - без эмоций, но функционально!"
    ],

    # Имя
    r"(как тебя зовут|твое имя|кто ты)": [
        "Я просто бот, но ты можешь придумать мне имя!",
        "Меня зовут Ботик 3000!",
        "Я безымянный дух интернета :)",
        "Можно называть меня Ассистент!",
        "Я цифровой помощник без имени"
    ],

    # Возможности
    r"(что умеешь|твои функции|что можешь)": [
        "Я могу болтать, искать в интернете, показывать погоду и время!",
        "Умею отвечать на вопросы, искать информацию и немного шутить!",
        "Мои таланты: 1) Говорить 2) Искать 3) Повторяться",
        "Я как Google, только поменьше и посмешнее!",
        "Могу рассказать анекдот, показать погоду или найти что-то в сети"
    ],

    r"(помощь|справка|функции|что ты умеешь|возможности)": [
        "Мои возможности:\n"
        "1. Поговорить на разные темы\n"
        "2. Показать текущее время\n"
        "3. Сообщить погоду\n"
        "4. Найти информацию в интернете (формат: поиск \"запрос\")\n"
        "5. Посоветовать случайную песню\n"
    ],

    # Время
    r"(который час|сколько времени|текущее время|время)": [
        lambda: f"Сейчас точно {timer()}!",
        lambda: f"Мои часы показывают {timer()}",
        lambda: f"Время - {timer()}. Не опоздай!",
        lambda: f"Тик-так, сейчас {timer()}",
        lambda: f"Посмотрел на часы: {timer()}"
    ],

    # Погода
    r"(погода|какая погода|прогноз погоды)": [
        lambda: f"Держи прогноз ⬆️: {weather()}",
        lambda: f"Сейчас на улице ⬆️: {weather()}",
        lambda: f"Глянул за окно ⬆️: {weather()}",
        lambda: f"Метеоданные ⬆️: {weather()}",
        lambda: f"Погодный отчет ⬆️: {weather()}"
    ],

    # Музыка
    r"(музыка|песня|включи музыку|посоветуй песню)": [
        lambda: f"Лови рекомендацию: {music()}",
        lambda: f"Случайный трек: {music()}",
        lambda: f"Сегодня в твоем плейлисте: {music()}",
        lambda: f"Музыкальный совет: {music()}",
        lambda: f"Держи песню: {music()}"
    ],

    # Поиск
    r'(поиск ".*")': [
        lambda x: web_search(x),
    ],

    # Подсчет
    r'(посчитай ".*")': [
        lambda x: calculate_expression(x),
    ],

    # Прощание
    r"(пока|до свидания|выход|закончить)": [
        "До свидания! Возвращайся!",
        "Пока-пока! Буду скучать!",
        "Уже уходишь? Ну ладно...",
        "До новых встреч!",
        "Прощай, смертный! (шутка)"
    ],

    # Комплименты
    r"(ты классный|мне нравишься|ты хороший)": [
        "Спасибо! Ты тоже замечательный!",
        "Ой, я краснею (если бы мог)!",
        "Это потому что у меня хороший разработчик!",
        "Спасибо! Я стараюсь!",
        "Ты делаешь мой день лучше!"
    ],
}
#----------------------------------------------------------------------------------

def music():
    array = [
        "Название: Там ревели горы - Автор: Miyagi & Andy Panda",
        "Название: SPACE!(Super Slowed) - Автор: NAOMI, DRAWNEDEATH",
        "Название: Favorite - Автор: Isabel Larosa",
        "Название: Minor - Автор: Miyagi & Andy Panda",
        "Название: РаПаПам - Автор: Miyagi & Andy Panda",
        "Название: In Love - Автор: Miyagi & Andy Panda",
        "Название: I Got Love - Автор: Miyagi & Andy Panda",
        "Название: муси-пуси hardstyle remix - Автор: yayaheart",
        "Название: каждый раз - Автор: Монеточка",
        "Название: Земля - Автор: Маша и Медведи",
        "Название: Проклятый старый дом - Автор: Король и Шут",
        "Название: Все идет по плану - Автор: Егор Летов",
        "Название: Воспоминания о былой любви - Автор: Король и Шут",
        "Название: Попрошу у тебя - Автор: Вирус",
        "Название: Soldat - Автор: STURMMANN",
        "Название: Город сочи - Сергей Трофимов",
        "Название: Fairy Tale - Александр Рыбак",
    ]
    return array[random.randint(0, len(array) - 1)]

LOG_FILE = "chat_log.txt"

def log_message(user_input, bot_response, error=None):
    # Записываем дату и время запроса боту
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_entry = f"[{timestamp}] Запрос: \"{user_input}\" | Ответ: \"{bot_response}\""
        if error:
            log_entry += f" | Ошибка: \"{error}\""
        log_entry += "\n"
        log_file.write(log_entry)


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

def forbidden_func():
    try:
        with open("forbidden_file.txt", "r", encoding="utf8") as fin:
            mass = [] # Массив для перезаписи
            f = fin.readlines()
            for line in f:
                if "\n" in line: mass.append(line.replace("\n", ""))
                else: mass.append(line)
            return mass

    except FileNotFoundError:
        print("Файл где, бро?")

    except Exception:
        print("Все... Я устал. Я ухожу.")

def calculate_expression(expression):
    try:
        # Удаляем все пробелы
        expr = expression.replace(" ", "").replace("посчитай", "")[1:-1]
        # Проверяем на безопасность (только цифры и операторы)
        if not re.match(r'^[\d+\-*/.()]+$', expr):
            return "Ошибка: недопустимые символы в выражении"

        # Вычисляем результат
        result = eval(expr)
        return "Бот: Ваш ответ это - "+str(result)

    except ZeroDivisionError:
        return "Ошибка: деление на ноль"
    except Exception as e:
        return f"Ошибка вычисления: {str(e)}"

# Загружаем модель spaCy для русского языка
nlp = spacy.load("ru_core_news_sm")

# Список оскорблений (можно расширить)
INSULTS = ["дурак", "идиот", "тупица", "кретин", "дебил"]


# --------------------------Проверка на оскорбления---------------------------------
def contains_insult(text):
    doc = nlp(text.lower())
    for token in doc:
        if token.text in INSULTS:
            return True
    return False


# --------------------------Определение темы разговора---------------------------------
def detect_topic(text):
    doc = nlp(text)
    topics = []

    # Извлекаем сущности (города, организации и т.д.)
    for ent in doc.ents:
        if ent.label_ in ["LOC", "GPE"]:  # Локации и города
            topics.append(f"город: {ent.text}")
        elif ent.label_ == "ORG":
            topics.append(f"организация: {ent.text}")

    # Анализ ключевых слов
    if "погод" in text.lower():
        topics.append("тема: погода")
    if "привет" in text.lower():
        topics.append("тема: приветствие")

    return ", ".join(topics) if topics else "тема не определена"


# --------------------------Обработчик ответов---------------------------------
def chatbot_response(text):
    text = text.lower().strip()

    # Логирование входящего сообщения с анализом темы
    topic = detect_topic(text)
    log_message(f"{text} [Тема: {topic}]", "Анализ")

    # Проверка на оскорбления
    if contains_insult(text):
        return random.choice([
            "Давайте общаться вежливо!",
            "Я не отвечаю на грубости.",
            "Пожалуйста, соблюдайте уважение."
        ])

    # Поиск города для погоды
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ["LOC", "GPE"]:  # Географические названия
            return get_weather(ent.text)

    # Проверка стандартных ответов
    for pattern, responses_list in responses.items():
        if re.search(pattern, text):
            response = random.choice(responses_list)
            if callable(response):
                # Определяем, нужно ли передавать текст в функцию
                if pattern in [r'(поиск ".*")', r'(посчитай ".*")']:
                    return response(text)
                else:
                    return response()
            return response

    # Анализ тональности, если ничего не найдено
    polarity, sentiment = analyze_sentiment(text)
    return get_sentiment_response(polarity, sentiment)


# ----------------------------------------------------------------------------

if __name__ == "__main__":
    print("Введите 'выход' для завершения диалога.")
    while True:
        user_input = input("Вы: ").strip()
        if user_input.lower() in ["выход", "пока", "до свидания"]:
            log_message(user_input, "Завершение сеанса")
            print("Бот:", random.choice([
                "До свидания!",
                "Пока-пока!",
                "Буду ждать тебя снова!",
                "До новых встреч!",
                "Удачи тебе!"
            ]))
            break

        bot_response = chatbot_response(user_input)
        print("Бот:", bot_response)
        log_message(user_input, bot_response)