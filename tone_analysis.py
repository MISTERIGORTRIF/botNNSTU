import random

from textblob import TextBlob
from translate import Translator


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