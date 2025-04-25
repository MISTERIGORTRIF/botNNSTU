import re

def calculate_expression(expression):
    try:
        # Удаляем все пробелы
        expr = expression.replace(" ", "").replace("посчитай", "")[1:-1]
        # Проверяем на безопасность (только цифры и операторы)
        if not re.match(r'^[\d+\-*/.()]+$', expr):
            return "Ошибка: недопустимые символы в выражении"

        # Вычисляем результат
        result = eval(expr)
        return "Бот: Ваш ответ это - "+str(result)

    except ZeroDivisionError:
        return "Ошибка: деление на ноль"
    except Exception as e:
        return f"Ошибка вычисления: {str(e)}"