# dubina/utils.py

import threading
from datetime import datetime
from colorama import Style, init, Fore

# Инициализация colorama.
init(autoreset=True)

# Глобальная блокировка для синхронизации вывода в консоль из разных потоков.
print_lock = threading.Lock()

def log(tag_color: str, tag_text: str, message: str):
    """
    Выводит потокобезопасное сообщение в консоль с временной меткой,
    тегом и текстом, окрашивая всю строку в заданный цвет.

    Args:
        tag_color (str): Цвет из colorama (например, Fore.CYAN).
        tag_text (str): Текст тега (например, "[SERVER]").
        message (str): Текст сообщения.
    """
    with print_lock:
        timestamp = datetime.now().strftime('%H:%M:%S')
        # Style.BRIGHT может быть частью tag_color, например `Style.BRIGHT + Fore.GREEN`
        # autoreset=True в init() позаботится о сбросе цвета.
        print(f"{tag_color}{timestamp} {tag_text} {message}")


