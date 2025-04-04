import re
import random

from logginnnn import log_message
from responses import responses

from tone_analysis import analyze_sentiment, get_sentiment_response


#--------------------------Обработчик ответов---------------------------------
def chatbot_response(text):
    text = text.lower().strip()

    # Сначала проверяем стандартные ответы
    for pattern, responses_list in responses.items():
        if re.search(pattern, text):
            response = random.choice(responses_list)
            if callable(response):
                if 'поиск' in pattern:
                    return response(text)
                return response()
            return response

    # Если стандартного ответа нет, анализируем тональность
    polarity, sentiment = analyze_sentiment(text)
    return get_sentiment_response(polarity, sentiment)
#----------------------------------------------------------------------------


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