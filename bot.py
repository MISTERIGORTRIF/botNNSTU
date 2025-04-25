import re
import random
from logginnnn import log_message
from responses import responses
from tone_analysis import analyze_sentiment, get_sentiment_response
import spacy

from weather import get_weather

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
                return response(text) if 'поиск' or "почитай" in pattern else response()
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