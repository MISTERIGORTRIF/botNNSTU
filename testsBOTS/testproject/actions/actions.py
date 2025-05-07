from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from datetime import datetime
import random
import webbrowser
from urllib.parse import quote
import requests
from dotenv import load_dotenv
import os
import time
from typing import Optional

load_dotenv()


class WeatherService:
    DEFAULT_CITY = "Нижний Новгород,RU"

    def __init__(self):
        self.api_key = os.getenv("OPEN_WEATHER_KEY")

    def get_weather_data(self, city: Optional[str] = None) -> Dict:
        """Получение данных о погоде с API"""
        city = f"{city},RU" if city else self.DEFAULT_CITY
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric&lang=ru"

        if not self.api_key:
            raise ValueError("API ключ не настроен")

        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Ошибка API: {response.status_code}")

        return response.json()

    def format_weather(self, data: Dict) -> str:
        """Форматирование данных о погоде в читаемый текст"""
        return (
            f"Погода в городе {data['name']}:\n"
            f"- Температура: {data['main']['temp']}°C (ощущается как {data['main']['feels_like']}°C)\n"
            f"- Описание: {data['weather'][0]['description'].capitalize()}\n"
            f"- Влажность: {data['main']['humidity']}%\n"
            f"- Скорость ветра: {data['wind']['speed']} м/с"
        )

    def get_default_weather(self) -> str:
        """Получение погоды для города по умолчанию"""
        try:
            data = self.get_weather_data()
            time.sleep(1)  # Задержка для имитации обработки
            return self.format_weather(data)
        except Exception as e:
            return f"Ошибка получения погоды: {str(e)}"

    def get_city_weather(self, city: str) -> str:
        """Получение погоды для указанного города"""
        try:
            if not city:
                return "Город не указан. " + self.get_default_weather()

            data = self.get_weather_data(city)
            time.sleep(1)
            return self.format_weather(data)
        except Exception as e:
            return f"Не удалось получить погоду для {city}: {str(e)}"


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

    def get_random_song(self) -> str:
        """Получение случайной песни из списка"""
        return random.choice(self.songs)


class ActionGetWeather(Action):
    def name(self) -> Text:
        return "action_get_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        weather_service = WeatherService()
        location = next(tracker.get_latest_entity_values("location"), None)

        if location:
            weather = weather_service.get_city_weather(location)
        else:
            weather = weather_service.get_default_weather()

        dispatcher.utter_message(text=weather)
        return []


class ActionGetTime(Action):
    def name(self) -> Text:
        return "action_get_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_time = datetime.now().strftime("%H:%M:%S")
        dispatcher.utter_message(text=f"Сейчас точно {current_time}!")
        return []


class ActionGetMusic(Action):
    def name(self) -> Text:
        return "action_get_music"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        music_service = MusicService()
        song = music_service.get_random_song()
        dispatcher.utter_message(text=f"Рекомендую: {song}")
        return []


class ActionSearch(Action):
    def name(self) -> Text:
        return "action_search"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        query = next(tracker.get_latest_entity_values("query"), None)
        if not query:
            dispatcher.utter_message(text="Не указан поисковый запрос")
            return []

        try:
            webbrowser.open(f"https://www.google.com/search?q={quote(query)}")
            dispatcher.utter_message(text=f"Ищу: {query}")
        except Exception as e:
            dispatcher.utter_message(text=f"Ошибка поиска: {str(e)}")

        return []


class ActionHandleInsult(Action):
    def name(self) -> Text:
        return "action_handle_insult"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        responses = [
            "Давайте общаться вежливо!",
            "Я не отвечаю на грубости.",
            "Пожалуйста, соблюдайте уважение."
        ]
        dispatcher.utter_message(text=random.choice(responses))
        return []