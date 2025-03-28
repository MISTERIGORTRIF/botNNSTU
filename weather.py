import requests
from dotenv import load_dotenv
import os
import time


def weather():
    try:
        load_dotenv() # Загрузили данные из env
        API_KEY = os.getenv("OPEN_WEATHER_KEY") # Выбрали ключик
        CITY = "Нижний Новгород,RU"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric&lang=ru" # Ссылочка на сайтик :3

        if API_KEY is None:
            raise ValueError("АПИ ИНОГДА КОКЕТНИЧАЕТ СО МНОЙ ПО-РУССКИ. 🔑🔑🔑🔑🔑")

        if requests.get(url).status_code != 200:
            raise ValueError("ЭЭЭЭЭЭЭ КУДА ПРЕЩЬ?? НЕ ВИДИШЬ КОД НЕ 200??? 💔💔💔")

    except Exception as e:
        return e
    else:
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
        print(f"Погода в городе {city}:")
        print(f"- Температура: {temp}°C (ощущается как {feels_like}°C)")
        print(f"- Описание: {weather_desc.capitalize()}")
        print(f"- Влажность: {humidity}%")
        print(f"- Скорость ветра: {wind_speed} м/с")
        # ----------------------------------------------

        # Костыль для вывода
        return ""