import socket
import threading
from colorama import Fore
from ..utils import log


class InternalApiServer(threading.Thread):
    """
    Мини-сервер, который запускается внутри основного сервера манипулятора.
    Он открывает TCP-порт, принимает ОДНО соединение от веб-сервера
    и транслирует ему в реальном времени обновления статуса.
    """

    def __init__(self, host: str, port: int):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.client_socket = None
        self.lock = threading.Lock()
        self._running = True

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(1)
            log(Fore.MAGENTA, "[INTERNAL-API]", f"Сервер внутреннего API запущен на {self.host}:{self.port}")
        except OSError as e:
            log(Fore.RED, "[INTERNAL-API]", f"Не удалось запустить сервер внутреннего API: {e}")
            return

        while self._running:
            try:
                # Ждем подключения веб-сервера
                conn, addr = server_socket.accept()
                log(Fore.MAGENTA, "[INTERNAL-API]", f"Веб-сервер подключился с {addr}")

                with self.lock:
                    self.client_socket = conn

                # Держим соединение, пока оно не разорвется
                while self._running:
                    # Проверяем, жив ли сокет, пытаясь прочитать из него
                    # Если клиент отвалился, recv вернет b''
                    data = conn.recv(1)
                    if not data:
                        break

            except (ConnectionResetError, BrokenPipeError, OSError):
                pass  # Обычная ситуация, если клиент отключается
            finally:
                with self.lock:
                    if self.client_socket:
                        self.client_socket.close()
                    self.client_socket = None
                if self._running:
                    log(Fore.YELLOW, "[INTERNAL-API]", "Веб-сервер отключился. Ожидание нового подключения...")

        server_socket.close()
        log(Fore.MAGENTA, "[INTERNAL-API]", "Сервер внутреннего API остановлен.")

    def send(self, message: str):
        """Отправляет сообщение подключенному веб-серверу."""
        with self.lock:
            if self.client_socket:
                try:
                    self.client_socket.sendall((message + '\n').encode('utf-8'))
                except (ConnectionResetError, BrokenPipeError, OSError):
                    # Если сокет сломался во время отправки
                    self.client_socket.close()
                    self.client_socket = None

    def stop(self):
        self._running = False
        # Создаем фейковое подключение к себе, чтобы разблокировать server_socket.accept()
        try:
            with socket.create_connection((self.host, self.port), timeout=0.1):
                pass
        except (socket.timeout, ConnectionRefusedError):
            pass
