import sqlite3
import os
import webbrowser
import requests
from dotenv import load_dotenv
import re
from datetime import datetime
from urllib.parse import quote
from textblob import TextBlob
from translate import Translator
import random
import logging
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


# Настройка логгера
logger = logging.getLogger(__name__)
load_dotenv()


# ==============================================
# КЛАСС ДЛЯ РАБОТЫ С БАЗОЙ ДАННЫХ
# ==============================================
class DatabaseManager:
    _instance = None

    def __new__(cls, db_name="rasa_bot.db"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db_name = db_name
            cls._instance.connection = None
            cls._instance._initialize_db()
        return cls._instance

    def _initialize_db(self):
        """Инициализация базы данных и создание таблиц"""
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()

            # Таблица для логов диалогов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dialog_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    bot_response TEXT NOT NULL,
                    intent TEXT,
                    sentiment_polarity REAL,
                    sentiment_label TEXT,
                    entities TEXT
                )
            """)

            # Таблица для песен
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS songs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    genre TEXT,
                    added_date TEXT NOT NULL,
                    UNIQUE(title, artist)
                )
            """)

            # Таблица для запросов погоды
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weather_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    city TEXT NOT NULL,
                    temperature REAL,
                    feels_like REAL,
                    description TEXT,
                    humidity INTEGER,
                    wind_speed REAL
                )
            """)

            # Таблица для пользователей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    message_count INTEGER DEFAULT 0
                )
            """)

            self.connection.commit()
            self._seed_initial_data()

        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def _seed_initial_data(self):
        """Заполнение начальными данными при первом запуске"""
        try:
            cursor = self.connection.cursor()

            # Проверяем, есть ли уже песни в базе
            cursor.execute("SELECT COUNT(*) FROM songs")
            count = cursor.fetchone()[0]

            if count == 0:
                initial_songs = [
                    ("Там ревели горы", "Miyagi & Andy Panda", "Rap"),
                    ("SPACE! (Super Slowed)", "NAOMI, DRAWNEDEATH", "Electronic"),
                    ("Favorite", "Isabel Larosa", "Pop"),
                    ("Minor", "Miyagi & Andy Panda", "Rap"),
                    ("РаПаПам", "Miyagi & Andy Panda", "Rap")
                ]

                for title, artist, genre in initial_songs:
                    self.add_song(title, artist, genre)

                logger.info("Initial songs data seeded successfully")

        except sqlite3.Error as e:
            logger.error(f"Error seeding initial data: {e}")

    def log_dialog(self, user_id: str, user_message: str, bot_response: str,
                   intent: str = None, polarity: float = None,
                   sentiment: str = None, entities: str = None):
        """Логирование диалога в базу данных"""
        try:
            cursor = self.connection.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Обновляем информацию о пользователе
            self._update_user_stats(user_id)

            cursor.execute("""
                INSERT INTO dialog_logs 
                (timestamp, user_id, user_message, bot_response, intent, 
                 sentiment_polarity, sentiment_label, entities)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, user_id, user_message, bot_response, intent,
                  polarity, sentiment, entities))

            self.connection.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Dialog logging error: {e}")
            return False

    def _update_user_stats(self, user_id: str):
        """Обновление статистики пользователя"""
        try:
            cursor = self.connection.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Проверяем, существует ли пользователь
            cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
            exists = cursor.fetchone()

            if exists:
                # Обновляем last_seen и увеличиваем счетчик сообщений
                cursor.execute("""
                    UPDATE users 
                    SET last_seen = ?, message_count = message_count + 1 
                    WHERE user_id = ?
                """, (now, user_id))
            else:
                # Создаем новую запись пользователя
                cursor.execute("""
                    INSERT INTO users (user_id, first_seen, last_seen, message_count)
                    VALUES (?, ?, ?, 1)
                """, (user_id, now, now))

            self.connection.commit()
        except sqlite3.Error as e:
            logger.error(f"User stats update error: {e}")

    def add_song(self, title: str, artist: str, genre: str = None):
        """Добавление песни в базу данных"""
        try:
            cursor = self.connection.cursor()
            added_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT OR IGNORE INTO songs (title, artist, genre, added_date)
                VALUES (?, ?, ?, ?)
            """, (title, artist, genre, added_date))

            self.connection.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Add song error: {e}")
            return False

    def get_random_song(self):
        """Получение случайной песни из базы данных"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT title, artist FROM songs 
                ORDER BY RANDOM() 
                LIMIT 1
            """)
            return cursor.fetchone()
        except sqlite3.Error as e:
            logger.error(f"Get random song error: {e}")
            return None

    def search_songs(self, query: str):
        """Поиск песен по запросу"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT title, artist FROM songs 
                WHERE title LIKE ? OR artist LIKE ?
                LIMIT 10
            """, (f"%{query}%", f"%{query}%"))
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Song search error: {e}")
            return []

    def log_weather_request(self, user_id: str, city: str, temperature: float,
                            feels_like: float, description: str,
                            humidity: int, wind_speed: float):
        """Логирование запроса погоды"""
        try:
            cursor = self.connection.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO weather_requests 
                (timestamp, user_id, city, temperature, feels_like, 
                 description, humidity, wind_speed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, user_id, city, temperature, feels_like,
                  description, humidity, wind_speed))

            self.connection.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Weather request logging error: {e}")
            return False

    def get_user_stats(self, user_id: str):
        """Получение статистики пользователя"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT first_seen, last_seen, message_count 
                FROM users 
                WHERE user_id = ?
            """, (user_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            logger.error(f"Get user stats error: {e}")
            return None

    def close(self):
        """Закрытие соединения с базой данных"""
        if self.connection:
            self.connection.close()
            self._instance = None


# Инициализация менеджера базы данных
db = DatabaseManager()


# ==============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==============================================
def forbidden_func():
    """Получение списка запрещенных слов"""
    try:
        with open("forbidden_file.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.warning("Forbidden words file not found")
        return []


def translate_to_english(text: str) -> str:
    """Перевод текста на английский для анализа тональности"""
    translator = Translator(to_lang="en", from_lang="ru")
    try:
        return translator.translate(text).lower()
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text


def analyze_sentiment(text: str) -> tuple:
    """Анализ тональности текста"""
    try:
        # Проверка на английские символы
        if any((65 <= ord(c) <= 90) or (97 <= ord(c) <= 122) for c in text):
            return 0.0, "neutral"

        text_en = translate_to_english(text)
        analysis = TextBlob(text_en)
        polarity = analysis.sentiment.polarity

        if polarity > 0.1:
            sentiment = "positive"
        elif polarity < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return polarity, sentiment
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        return 0.0, "neutral"


def get_sentiment_response(polarity: float, sentiment: str) -> str:
    """Генерация ответа на основе тональности"""
    responses = {
        "error": ["По русски пиши пожалуйста."],
        "positive": [
            "Я чувствую позитив! Оценка тональности: {:.2f}",
            "Какой позитивный настрой! Тональность: {:.2f}",
            "Ваш энтузиазм заразителен! Оценка: {:.2f}"
        ],
        "negative": [
            "Мне жаль, что вам плохо... Оценка тональности: {:.2f}",
            "Похоже, вам грустно. Тональность: {:.2f}",
            "Я здесь, чтобы помочь. Оценка настроения: {:.2f}"
        ],
        "neutral": [
            "Понятно. Оценка тональности: {:.2f}",
            "Интересно. Тональность сообщения: {:.2f}",
            "Спасибо за сообщение. Оценка: {:.2f}"
        ]
    }
    return random.choice(responses.get(sentiment, responses["neutral"])).format(polarity)


# ==============================================
# КЛАССЫ ДЕЙСТВИЙ RASA
# ==============================================
class ActionLogResponse(Action):
    """Действие для логирования диалога в БД"""

    def name(self) -> Text:
        return "action_log_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            user_id = tracker.sender_id
            user_message = tracker.latest_message.get("text", "")
            intent = tracker.latest_message.get("intent", {}).get("name")
            entities = str(tracker.latest_message.get("entities", []))

            # Получаем последний ответ бота
            bot_response = next(
                (e.get("text") for e in reversed(tracker.events)
                 if e.get("event") == "bot" and e.get("text")),
                "[No response]"
            )

            # Логируем в базу данных
            db.log_dialog(
                user_id=user_id,
                user_message=user_message,
                bot_response=bot_response,
                intent=intent,
                entities=entities
            )

        except Exception as e:
            logger.error(f"Log response error: {e}")

        return []


class ActionRandomSong(Action):
    """Действие для получения случайной песни"""

    def name(self) -> Text:
        return "action_random_song"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            song = db.get_random_song()
            if song:
                response = f"🎵 Случайная песня: {song['title']} - {song['artist']}"
            else:
                response = "Извините, не удалось найти песни. Попробуйте позже."

            dispatcher.utter_message(text=response)

        except Exception as e:
            logger.error(f"Random song error: {e}")
            dispatcher.utter_message(text="Произошла ошибка при выборе песни")

        return []


class ActionSearchSongs(Action):
    """Действие для поиска песен"""

    def name(self) -> Text:
        return "action_search_songs"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            query = next(tracker.get_latest_entity_values("song_query"), None)
            if not query:
                dispatcher.utter_message(text="Укажите что искать, например: 'найди песню Майки'")
                return []

            songs = db.search_songs(query)
            if songs:
                response = "🔍 Найденные песни:\n" + "\n".join(
                    f"- {song['title']} ({song['artist']})" for song in songs
                )
            else:
                response = f"По запросу '{query}' ничего не найдено"

            dispatcher.utter_message(text=response)

        except Exception as e:
            logger.error(f"Song search error: {e}")
            dispatcher.utter_message(text="Произошла ошибка при поиске песен")

        return []


class ActionGetWeather(Action):
    """Действие для получения погоды"""

    def name(self) -> Text:
        return "action_get_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            api_key = os.getenv("OPEN_WEATHER_KEY")
            city = next(tracker.get_latest_entity_values("city"), None)
            user_id = tracker.sender_id

            if not city:
                dispatcher.utter_message(text="Укажите город, например: 'Погода в Москве'")
                return []

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

                # Логируем запрос погоды
                db.log_weather_request(
                    user_id=user_id,
                    city=data['name'],
                    temperature=data['main']['temp'],
                    feels_like=data['main']['feels_like'],
                    description=data['weather'][0]['description'],
                    humidity=data['main']['humidity'],
                    wind_speed=data['wind']['speed']
                )

                dispatcher.utter_message(text=weather_info)
            else:
                dispatcher.utter_message(text=f"Город '{city}' не найден или сервис недоступен")

        except Exception as e:
            logger.error(f"Weather error: {e}")
            dispatcher.utter_message(text="Сервис погоды временно недоступен")

        return []


class ActionCalculate(Action):
    """Действие для вычисления математических выражений"""

    def name(self) -> Text:
        return "action_calculate"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            message = tracker.latest_message.get("text", "")
            expr = re.search(r"(\d+)\s*([+-\/*])\s*(\d+)", message)

            if expr:
                a, op, b = map(str.strip, expr.groups())
                a, b = int(a), int(b)

                if op == '+':
                    result = a + b
                elif op == '-':
                    result = a - b
                elif op == '*':
                    result = a * b
                elif op == '/':
                    result = a / b if b != 0 else "∞ (деление на ноль)"

                dispatcher.utter_message(text=f"Результат: {result}")
            else:
                dispatcher.utter_message(text="Не понял выражение. Пример: 'Посчитай 2+2'")

        except Exception as e:
            logger.error(f"Calculation error: {e}")
            dispatcher.utter_message(text="Ошибка при вычислении")

        return []


class ActionGetTime(Action):
    """Действие для получения текущего времени"""

    def name(self) -> Text:
        return "action_get_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_time = datetime.now().strftime("%H:%M:%S")
        dispatcher.utter_message(text=f"Сейчас {current_time}")
        return []


class ActionAnalyzeSentiment(Action):
    """Действие для анализа тональности сообщения"""

    def name(self) -> Text:
        return "action_analyze_sentiment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            user_id = tracker.sender_id
            message = tracker.latest_message.get("text", "")
            intent = tracker.latest_message.get("intent", {}).get("name")

            polarity, sentiment = analyze_sentiment(message)
            response = get_sentiment_response(polarity, sentiment)

            # Логируем с информацией о тональности
            db.log_dialog(
                user_id=user_id,
                user_message=message,
                bot_response=response,
                intent=intent,
                polarity=polarity,
                sentiment=sentiment
            )

            dispatcher.utter_message(text=response)

        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            dispatcher.utter_message(text="Не удалось проанализировать сообщение")

        return []


class ActionWebSearch(Action):
    """Действие для поиска в интернете"""

    def name(self) -> Text:
        return "action_web_search"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            message = tracker.latest_message.get("text", "")

            if message.lower().startswith('поиск "') and message.count('"') >= 2:
                query = message.split('"')[1]
                forbidden = forbidden_func()

                # Проверка на запрещенные слова
                forbidden_words = [word for word in query.split() if word in forbidden]
                if forbidden_words:
                    response = f"Запрос содержит запрещенные слова: {', '.join(forbidden_words)}"
                else:
                    webbrowser.open(f"https://www.google.com/search?q={quote(query)}")
                    response = f"🔍 Результаты поиска для: {query}"
            else:
                response = "Используйте формат: поиск \"ваш запрос\""

            dispatcher.utter_message(text=response)

        except Exception as e:
            logger.error(f"Web search error: {e}")
            dispatcher.utter_message(text="Ошибка при выполнении поиска")

        return []


class ActionUserStats(Action):
    """Действие для показа статистики пользователя"""

    def name(self) -> Text:
        return "action_user_stats"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            user_id = tracker.sender_id
            stats = db.get_user_stats(user_id)

            if stats:
                response = (
                    f"📊 Ваша статистика:\n"
                    f"- Первое сообщение: {stats['first_seen']}\n"
                    f"- Последняя активность: {stats['last_seen']}\n"
                    f"- Всего сообщений: {stats['message_count']}"
                )
            else:
                response = "Статистика не найдена"

            dispatcher.utter_message(text=response)

        except Exception as e:
            logger.error(f"User stats error: {e}")
            dispatcher.utter_message(text="Не удалось получить статистику")

        return []