from datetime import datetime

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
