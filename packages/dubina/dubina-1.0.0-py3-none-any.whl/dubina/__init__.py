"""
Библиотека 'dubina' для централизованного управления манипуляторами
с поддержкой очереди клиентов и веб-интерфейсом.
"""

# --- Публичный API для пользователя ---

# 1. Импортируем фабричную функцию для создания сервера манипулятора.
#    Пример использования:
#    from dubina import Server
#    s = Server("sd1", internal_port=50055)
#    s.start()
from .server_factory import create_server as Server

# 2. Импортируем готовый клиентский класс для манипулятора SD1.
#    Пример использования:
#    from dubina import SD1
#    arm = SD1(host="127.0.0.1", port=5000, name="Ivanov")
from .manipulators.sd1.client import Client as SD1

# 3. Импортируем класс для запуска веб-страницы.
#    Пример использования:
#    from dubina import WebPage
#    page = WebPage(connect_to_port=50055)
#    page.start()
from .web.server import WebServer as WebPage


# Версия библиотеки
__version__ = "1.0.0"


