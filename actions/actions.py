import webbrowser
import requests
import os
from dotenv import load_dotenv
import re
from datetime import datetime
import logging
from urllib.parse import quote
from textblob import TextBlob
from translate import Translator
import random
from typing import Any, List, Text, Dict
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

logger = logging.getLogger(__name__)
load_dotenv()

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


class ActionGetWeather(Action):
    def name(self) -> Text:
        return "action_get_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        api_key = os.getenv("OPEN_WEATHER_KEY")
        city = next(tracker.get_latest_entity_values("city"), None)

        if not city:
            dispatcher.utter_message("Укажите город, например: 'Погода в Москве'")
            return []

        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city},RU&appid={api_key}&units=metric&lang=ru"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                weather_info = (
                    f"Погода в городе {data['name']}:\n"
                    f"- Температура: {data['main']['temp']}°C\n"
                    f"- Ощущается как: {data['main']['feels_like']}°C\n"
                    f"- Описание: {data['weather'][0]['description'].capitalize()}\n"
                    f"- Влажность: {data['main']['humidity']}%\n"
                    f"- Ветер: {data['wind']['speed']} м/с"
                )
                dispatcher.utter_message(weather_info)
            else:
                dispatcher.utter_message(f"Ошибка: город '{city}' не найден или сервис недоступен")

        except Exception as e:
            logger.error(f"Weather API error: {str(e)}")
            dispatcher.utter_message("Сервис погоды временно недоступен")

        return []


class ActionCalculate(Action):
    def name(self) -> Text:
        return "action_calculate"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = tracker.latest_message.get("text")
        try:
            # Безопасное вычисление простых выражений
            expr = re.search(r"(\d+)\s*([+-\/*])\s*(\d+)", message)
            if expr:
                a, op, b = expr.groups()
                a, b = int(a), int(b)

                if op == '+':
                    result = a + b
                elif op == '-':
                    result = a - b
                elif op == '*':
                    result = a * b
                elif op == '/':
                    result = a / b if b != 0 else "∞"

                dispatcher.utter_message(f"Результат: {result}")
            else:
                dispatcher.utter_message("Не понял выражение. Пример: 'Посчитай 2+2'")

        except Exception as e:
            logger.error(f"Calculation error: {str(e)}")
            dispatcher.utter_message("Ошибка вычисления")

        return []


class ActionGetTime(Action):
    def name(self) -> Text:
        return "action_get_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_time = datetime.now().strftime("%H:%M:%S")
        dispatcher.utter_message(f"Сейчас {current_time}")
        return []


class ActionAnalyzeSentiment(Action):
    def name(self) -> str:
        return "action_analyze_sentiment"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict):
        message = tracker.latest_message.get("text")

        # Выполняем анализ тональности
        polarity, sentiment = analyze_sentiment(message)

        # Получаем ответ в зависимости от тональности
        sentiment_response = get_sentiment_response(polarity, sentiment)

        # Отправляем сообщение с анализом тональности
        dispatcher.utter_message(text=sentiment_response)

        return []


class ActionWebSearch(Action):
    def name(self) -> Text:
        return "action_web_search"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Получаем последнее сообщение пользователя
        message = tracker.latest_message.get("text")

        result = self._perform_search(message)

        dispatcher.utter_message(result)  # Отправляем результат в чат
        return []

    def _perform_search(self, command: Text) -> Text:
        """Выполняет поиск в интернете через webbrowser"""
        try:
            # Проверяем, начинается ли команда с "поиск " и содержит ли она кавычки
            if command.lower().startswith('поиск "') and command.count('"') >= 2:
                # Извлекаем текст между кавычками
                query = command.split('"')[1]

                forbidden = forbidden_func()  # Получаем запрещенные слова
                string_forbidden = ""  # Для формирования запрещенной строки

                # Проверка на запрещенные слова в запросе
                if len(query.split()) > 1:
                    for word in query.split():
                        if word in forbidden:
                            string_forbidden += word + " "

                elif query in forbidden:
                    raise ValueError(f"Ты че... Я был о тебе лучшего мнения, чел... \nКакие {query}? Ты серьезно?!")

                # Если есть запрещенные слова, выводим ошибку
                if string_forbidden != "":
                    raise ValueError(
                        f"Ты че... Я был о тебе лучшего мнения, чел... \nКакие {string_forbidden}? Ты серьезно?!")

                # Открываем результаты поиска в браузере
                webbrowser.open(f"https://www.google.com/search?q={quote(query)}")
                return f"Открываю результаты для: {query}"

            return "Неверный формат. Используйте: поиск \"запрос\""

        except Exception as e:
            return f"Ошибка поиска: {str(e)}"


class ActionRandomSong(Action):
    def name(self) -> str:
        return "action_random_song"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        songs = [
            "Там ревели горы - Miyagi & Andy Panda",
            "SPACE!(Super Slowed) - NAOMI, DRAWNEDEATH",
            "Favorite - Isabel Larosa",
            "Minor - Miyagi & Andy Panda",
            "РаПаПам - Miyagi & Andy Panda",
            "In Love - Miyagi & Andy Panda",
            "I Got Love - Miyagi & Andy Panda",
            "муси-пуси hardstyle remix - yayaheart",
            "каждый раз - Монеточка",
            "Земля - Маша и Медведи",
            "Проклятый старый дом - Король и Шут",
            "Все идет по плану - Егор Летов",
            "Воспоминания о былой любви - Король и Шут",
            "Попрошу у тебя - Вирус",
            "Soldat - STURMMANN",
            "Город Сочи - Сергей Трофимов",
            "Fairy Tale - Александр Рыбак",
        ]

        if not songs:
            dispatcher.utter_message(text="Список песен пуст. Пожалуйста, добавьте песни.")
            return []

        song = random.choice(songs)
        dispatcher.utter_message(text=f"🎵 Случайная песня: {song}")

        return []
