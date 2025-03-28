
def forbidden_func():
    try:
        with open("forbidden_file.txt", "r", encoding="utf8") as fin:
            mass = [] # Массив для перезаписи
            f = fin.readlines()
            for line in f:
                if "\n" in line: mass.append(line.replace("\n", ""))
                else: mass.append(line)
            return mass

    except FileNotFoundError:
        print("Файл где, бро?")

    except Exception:
        print("Все... Я устал. Я ухожу.")