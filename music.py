import random


def music():
    array = [
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
    return array[random.randint(0, len(array) - 1)]