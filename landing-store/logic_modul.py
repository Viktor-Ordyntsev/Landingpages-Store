import os
import shutil
import zipfile
import socket


def Unzipping(zip_filename: str) -> bool:
    """ Функция для разархивирование zip-файлов. Получает на вход название файла, 
    в результате создается директория с таким же названием, Функция возращает булевое значение."""
    try:
        # Распаковка zip-файла
        zf = zipfile.ZipFile(f"pages/{zip_filename}")
        zf.extractall('pages')

        # Удаление сервисной директории
        shutil.rmtree(os.path.join(os.path.abspath(os.path.dirname(
            __file__)), 'pages/__MACOSX'))

        # Исправление название дириктори
        Files = os.listdir("pages/")
        for file in Files:
            if (file != zip_filename):
                if (zip_filename.split(".")[0] in file):
                    os.rename(f"pages/{file}",
                              f"pages/{zip_filename.split('.')[0]}")
                    return True
    except:
        return False


def Finding_and_changing_index_file(zip_filename: str) -> bool:
    """ Функция поиска и измение файла индексации. На вход получает название zip-файла. 
    В результате, файл индексации именуется 'index'. Функия возвращяет булевое значение. """
    try:
        # Получаем путь к рабочей директории
        directory = f"pages/{zip_filename.split('.')[0]}"

        # Список всех файлов
        Files = os.listdir(directory)

        # Переименовываем файл индексации
        for file in Files:
            file_sp = file.split(".")
            if (file_sp[0] == "index"):
                return True
            if ("page" in file_sp[0]):
                os.rename(
                    f"pages/{zip_filename.split('.')[0]}/{file}", f"pages/{zip_filename.split('.')[0]}/index.html")
                return True
    except:
        return False


def Domain_check(domain: str) -> bool:
    """Функция для проверки привязанности доменна к серверу. 
    На вход подается строка - имя домена.
    На выходе булевое значение"""
    try:
        # Резолвим домен, получай ipv4
        ip_v4_lst = socket.gethostbyname_ex(domain)

        # Сравниваем с ip полученным из переменных окружения
        if (os.environ["IP_ADDRESS"] in ip_v4_lst[2]):
            return True
        else:
            return False
    except:
        return False


def Cyrillic_to_Punycode_conversion(Cyrillic_domain: str) -> str:
    return Cyrillic_domain.encode('idna').decode()


def Checking_domain_foк_Cyrillic(Cyrillic_domain: str) -> bool:
    alphabet = {"а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л", "м", "н", "о",
                "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я"}

    return bool(alphabet.intersection(set(Cyrillic_domain.lower())))
