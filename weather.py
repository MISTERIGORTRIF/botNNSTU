import requests
from dotenv import load_dotenv
import os
import time


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