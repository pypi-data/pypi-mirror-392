import socket
import threading
import os
import time
from colorama import Fore
from flask import Flask, render_template
from flask_socketio import SocketIO

from dubina.utils import log
from dubina.locale.ru import MESSAGES

# --- Константы для веб-сервера ---
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 7000
DEFAULT_TITLE = "Статус манипулятора"
INTERNAL_API_HOST = '127.0.0.1'


class WebServer:
    """
    Класс, инкапсулирующий веб-сервер на Flask и SocketIO.
    """

    # --- ИСПРАВЛЕНИЕ В КОНСТРУКТОРЕ ---
    def __init__(self,
                 host: str = DEFAULT_HOST,
                 port: int = DEFAULT_PORT,
                 title_message: str = DEFAULT_TITLE,
                 connect_to_port: int = None):

        if not connect_to_port:
            raise ValueError("Необходимо указать порт для подключения к серверу манипулятора (connect_to_port).")

        self.host = host
        self.port = port
        self.title_message = title_message
        self.connect_to_port = connect_to_port

        template_folder = os.path.join(os.path.dirname(__file__), 'templates')
        static_folder = os.path.join(os.path.dirname(__file__), 'static')

        self.app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
        self.app.logger.disabled = True
        import logging
        log_werkzeug = logging.getLogger('werkzeug')
        log_werkzeug.disabled = True

        self.socketio = SocketIO(self.app, async_mode='threading')

        self._internal_client_thread = None
        self._register_routes()

    def _register_routes(self):
        """Регистрирует обработчики HTTP-запросов и событий SocketIO."""

        @self.app.route('/')
        def index():
            return render_template('index.html', title_message=self.title_message)

        @self.socketio.on('connect')
        def handle_connect():
            log(Fore.GREEN, MESSAGES.T.WEB, MESSAGES.WEB.BROWSER_CONNECTED)

    def _internal_client_worker(self):
        """
        Метод, который работает в фоновом потоке, подключается к серверу
        манипулятора и получает от него данные.
        """
        log(Fore.CYAN, MESSAGES.T.WEB,
            MESSAGES.WEB.TCP_LISTENER_STARTED.format(host=INTERNAL_API_HOST, port=self.connect_to_port))

        while True:  # Цикл для автоматического переподключения
            try:
                sock = socket.create_connection((INTERNAL_API_HOST, self.connect_to_port))
                log(Fore.GREEN, MESSAGES.T.WEB, MESSAGES.WEB.TCP_CONNECTION_SUCCESS)

                # Читаем данные из сокета построчно
                buffer = ""
                while True:
                    data = sock.recv(1024).decode('utf-8')
                    if not data:
                        raise ConnectionError("Соединение разорвано сервером.")

                    buffer += data
                    while '\n' in buffer:
                        message, buffer = buffer.split('\n', 1)
                        self._process_internal_message(message.strip())

            except (ConnectionRefusedError, ConnectionError, TimeoutError) as e:
                log(Fore.YELLOW, MESSAGES.T.WEB, MESSAGES.WEB.TCP_CONNECTION_LOST)
                time.sleep(5)  # Ждем 5 секунд перед попыткой переподключения
            except Exception as e:
                log(Fore.RED, MESSAGES.T.WEB, MESSAGES.WEB.TCP_CONNECTION_ERROR.format(error=e))
                time.sleep(5)

    def _process_internal_message(self, message: str):
        """
        Парсит сообщение от сервера манипулятора и пересылает
        в браузеры по WebSocket.
        """
        try:
            msg_type, payload = message.split(':', 1)

            if msg_type == 'QUEUE':
                queue = payload.split(',') if payload else []
                self.socketio.emit('queue_update', {'queue': queue})

            elif msg_type == 'LOG':
                user, command, status = payload.split(':', 2)
                self.socketio.emit('log_update', {'user': user, 'command': command, 'status': status})

        except ValueError:
            pass

    def start(self):
        """Запускает веб-сервер и все фоновые процессы."""
        # 1. Запускаем клиент внутреннего API в фоновом потоке
        self._internal_client_thread = threading.Thread(target=self._internal_client_worker, daemon=True)
        self._internal_client_thread.start()

        # 2. Запускаем Flask-сервер
        log(Fore.CYAN, MESSAGES.T.WEB, MESSAGES.WEB.STARTING.format(host=self.host, port=self.port))
        try:
            self.socketio.run(self.app, host=self.host, port=self.port, allow_unsafe_werkzeug=True, debug=False,
                              log_output=False)
        except OSError as e:
            log(Fore.RED, MESSAGES.T.WEB, MESSAGES.WEB.START_ERROR.format(error=e))
        except KeyboardInterrupt:
            pass  # Просто выходим, основная обработка будет в скрипте запуска
        finally:
            log(Fore.CYAN, MESSAGES.T.WEB, MESSAGES.WEB.STOPPING)
