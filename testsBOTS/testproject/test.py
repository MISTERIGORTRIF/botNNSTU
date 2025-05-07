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


class WeatherService:
    DEFAULT_CITY = "Нижний Новгород,RU"

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPEN_WEATHER_KEY")

    def get_weather_data(self, city=None):
        city = f"{city},RU" if city else self.DEFAULT_CITY
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric&lang=ru"

        if not self.api_key:
            raise ValueError("АПИ ключ не найден")

        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Ошибка API: {response.status_code}")

        return response.json()

    def format_weather(self, data):
        return (
            f"Погода в городе {data['name']}:\n"
            f"- Температура: {data['main']['temp']}°C (ощущается как {data['main']['feels_like']}°C)\n"
            f"- Описание: {data['weather'][0]['description'].capitalize()}\n"
            f"- Влажность: {data['main']['humidity']}%\n"
            f"- Скорость ветра: {data['wind']['speed']} м/с"
        )

    def get_default_weather(self):
        try:
            data = self.get_weather_data()
            time.sleep(2)
            return self.format_weather(data)
        except Exception as e:
            return str(e)

    def get_city_weather(self, city):
        try:
            if not city:
                print("Бот: Не знаю такого... Держи вот Нижний Новгород.")
                return self.get_default_weather()

            data = self.get_weather_data(city)
            time.sleep(2)
            return self.format_weather(data)
        except Exception as e:
            return str(e)


class SentimentAnalyzer:
    def __init__(self):
        self.translator = Translator(to_lang="en", from_lang="ru")

    def translate_to_english(self, text):
        try:
            return self.translator.translate(text).lower()
        except:
            return text

    def analyze_sentiment(self, text):
        try:
            if any((65 <= ord(char) <= 90) or (97 <= ord(char) <= 122) for char in text):
                return 0.0, "error"

            text = self.translate_to_english(text)
            analysis = TextBlob(text)
            polarity = analysis.sentiment.polarity

            if polarity > 0.1:
                sentiment = "позитивный"
            elif polarity < -0.1:
                sentiment = "негативный"
            else:
                sentiment = "нейтральный"

            return polarity, sentiment
        except Exception as e:
            print(f"Ошибка анализа тональности: {str(e)}")
            return 0.0, "нейтральный"

    def get_sentiment_response(self, polarity, sentiment):
        responses = {
            "error": ["По русски пиши пожалуйста."],
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


class MusicService:
    def __init__(self):
        self.songs = [
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

    def get_random_song(self):
        return random.choice(self.songs)


class Utils:
    @staticmethod
    def timer():
        return datetime.now().strftime("%H:%M:%S")

    @staticmethod
    def calculate_expression(expression):
        try:
            expr = expression.replace(" ", "").replace("посчитай", "")[1:-1]
            if not re.match(r'^[\d+\-*/.()]+$', expr):
                return "Ошибка: недопустимые символы в выражении"
            return f"Бот: Ваш ответ это - {eval(expr)}"
        except ZeroDivisionError:
            return "Ошибка: деление на ноль"
        except Exception as e:
            return f"Ошибка вычисления: {str(e)}"


class WebService:
    def __init__(self):
        self.forbidden_words = self.load_forbidden_words()

    def load_forbidden_words(self):
        try:
            with open("forbidden_file.txt", "r", encoding="utf8") as fin:
                return [line.strip() for line in fin if line.strip()]
        except FileNotFoundError:
            print("Файл с запрещенными словами не найден")
            return []
        except Exception as e:
            print(f"Ошибка чтения файла: {str(e)}")
            return []

    def search(self, command):
        try:
            if command.lower().startswith('поиск "') and command.count('"') >= 2:
                query = command.split('"')[1]
                forbidden_words = [word for word in self.forbidden_words if word in query]

                if forbidden_words:
                    raise ValueError(
                        f"Ты че... Я был о тебе лучшего мнения, чел...\n"
                        f"Какие {' '.join(forbidden_words)}? Ты серьезно?!"
                    )

                webbrowser.open(f"https://www.google.com/search?q={quote(query)}")
                return f"Открываю результаты для: {query}"
            return "Неверный формат. Используйте: поиск \"запрос\""
        except Exception as e:
            return f"Ошибка поиска: {str(e)}"


class NLPProcessor:
    def __init__(self):
        self.nlp = spacy.load("ru_core_news_sm")
        self.insults = ["дурак", "идиот", "тупица", "кретин", "дебил"]

    def contains_insult(self, text):
        doc = self.nlp(text.lower())
        return any(token.text in self.insults for token in doc)

    def detect_topic(self, text):
        doc = self.nlp(text)
        topics = []

        for ent in doc.ents:
            if ent.label_ in ["LOC", "GPE"]:
                topics.append(f"город: {ent.text}")
            elif ent.label_ == "ORG":
                topics.append(f"организация: {ent.text}")

        text_lower = text.lower()
        if "погод" in text_lower:
            topics.append("тема: погода")
        if "привет" in text_lower:
            topics.append("тема: приветствие")

        return ", ".join(topics) if topics else "тема не определена"


class Logger:
    def __init__(self, log_file="chat_log.txt"):
        self.log_file = log_file

    def log(self, user_input, bot_response, error=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a", encoding="utf-8") as log_file:
            log_entry = f"[{timestamp}] Запрос: \"{user_input}\" | Ответ: \"{bot_response}\""
            if error:
                log_entry += f" | Ошибка: \"{error}\""
            log_entry += "\n"
            log_file.write(log_entry)


class ChatBot:
    def __init__(self):
        self.weather_service = WeatherService()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.music_service = MusicService()
        self.utils = Utils()
        self.web_service = WebService()
        self.nlp_processor = NLPProcessor()
        self.logger = Logger()

        self.responses = self._init_responses()

    def _init_responses(self):
        return {
            # Приветствия
            r"(привет|здравствуй|хай|здаров)$": [
                "Привет-привет! Как дела?",
                "Здравствуй! Рад тебя видеть!",
                "Приветствую! Чем могу помочь?",
            ],

            # Как дела
            r"(как дела|как ты|как жизнь|как сам)$": [
                "Отлично! А у тебя?",
                "Как в сказке! Только вот дракона нет...",
                "Лучше всех! Ну почти :)",
            ],

            # Имя
            r"(как тебя зовут|твое имя|кто ты)$": [
                "Я просто бот, но ты можешь придумать мне имя!",
                "Меня зовут Ботик 3000!",
                "Я безымянный дух интернета :)",
            ],

            # Возможности
            r"(что умеешь|твои функции|что можешь)$": [
                "Я могу болтать, искать в интернете, показывать погоду и время!",
                "Умею отвечать на вопросы, искать информацию и немного шутить!",
            ],

            # Помощь
            r"(помощь|справка|функции|что ты умеешь|возможности)$": [
                "Мои возможности:\n"
                "1. Поговорить на разные темы\n"
                "2. Показать текущее время\n"
                "3. Сообщить погоду\n"
                "4. Найти информацию в интернете (формат: поиск \"запрос\")\n"
                "5. Посоветовать случайную песню\n"
            ],

            # Время
            r"(который час|сколько времени|текущее время|время)$": [
                lambda: f"Сейчас точно {self.utils.timer()}!",
                lambda: f"Мои часы показывают {self.utils.timer()}",
            ],

            # Погода (общий запрос)
            r"(погода|какая погода|прогноз погоды)$": [  # Добавил $ для точного соответствия
                lambda: f"Держи прогноз ⬆️: {self.weather_service.get_default_weather()}",
                lambda: f"Сейчас на улице ⬆️: {self.weather_service.get_default_weather()}",
            ],

            # Музыка
            r"(музыка|песня|включи музыку|посоветуй песню)$": [
                lambda: f"Лови рекомендацию: {self.music_service.get_random_song()}",
                lambda: f"Случайный трек: {self.music_service.get_random_song()}",
            ],

            # Поиск
            r'(поиск ".*")$': [
                lambda x: self.web_service.search(x),
            ],

            # Подсчет
            r'(посчитай ".*")$': [
                lambda x: self.utils.calculate_expression(x),
            ],

            # Прощание
            r"(пока|до свидания|выход|закончить)$": [
                "До свидания! Возвращайся!",
                "Пока-пока! Буду скучать!",
            ],

            # Комплименты
            r"(ты классный|мне нравишься|ты хороший)$": [
                "Спасибо! Ты тоже замечательный!",
                "Ой, я краснею (если бы мог)!",
            ],
        }

    def process_message(self, text):
        text = text.lower().strip()
        topic = self.nlp_processor.detect_topic(text)
        self.logger.log(f"{text} [Тема: {topic}]", "Анализ")

        # Проверка на оскорбления
        if self.nlp_processor.contains_insult(text):
            return random.choice([
                "Давайте общаться вежливо!",
                "Я не отвечаю на грубости.",
                "Пожалуйста, соблюдайте уважение."
            ])

        # Обработка запросов с городами (включая варианты "погода Балахна", "погода в Балахна")
        doc = self.nlp_processor.nlp(text)
        if "погода" in text:
            cities = [ent.text for ent in doc.ents if ent.label_ in ["LOC", "GPE"]]
            if cities:
                return self.weather_service.get_city_weather(cities[0])
            # Если город не распознан, но есть слово после "погода"
            words = text.split()
            if len(words) > 1 and words[0] == "погода":
                city = ' '.join(words[1:])
                return self.weather_service.get_city_weather(city)

        # Проверка стандартных ответов (только для точных соответствий)
        for pattern, responses_list in self.responses.items():
            if re.fullmatch(pattern, text):
                response = random.choice(responses_list)
                if callable(response):
                    if pattern in [r'(поиск ".*")$', r'(посчитай ".*")$']:
                        return response(text)
                    return response()
                return response

        # Анализ тональности, если ничего не найдено
        polarity, sentiment = self.sentiment_analyzer.analyze_sentiment(text)
        return self.sentiment_analyzer.get_sentiment_response(polarity, sentiment)


if __name__ == "__main__":
    bot = ChatBot()
    print("Введите 'выход' для завершения диалога.")

    while True:
        user_input = input("Вы: ").strip()
        if user_input.lower() in ["выход", "пока", "до свидания"]:
            bot.logger.log(user_input, "Завершение сеанса")
            print("Бот:", random.choice([
                "До свидания!",
                "Пока-пока!",
                "Буду ждать тебя снова!",
            ]))
            break

        bot_response = bot.process_message(user_input)
        print("Бот:", bot_response)
        bot.logger.log(user_input, bot_response)