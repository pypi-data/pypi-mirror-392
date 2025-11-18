import socket
import threading
from colorama import Fore, Style

from dubina.utils import log
from dubina.locale.ru import MESSAGES
from dubina.remote.protocol import Q_CMD, Q_RSP, SEPARATOR


class BaseClient:
    """
    Базовый клиент, который умеет подключаться к серверу,
    регистрироваться в очереди и ждать своей очереди на управление.
    """

    def __init__(self, host: str, port: int, name: str):
        self.host = host
        self.port = port
        self.name = name
        self._sock = None
        self._is_active = False
        self._response_lock = threading.Lock()
        self._last_response = ""
        self._response_event = threading.Event()
        self._listener_thread = None
        self._is_connected = False

        self._connect_and_register()

    def _connect_and_register(self):
        """Выполняет подключение, запуск потока-слушателя и ожидание очереди."""
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.connect((self.host, self.port))
            self._is_connected = True
            log(Fore.GREEN, MESSAGES.T.CLIENT, MESSAGES.CLIENT.CONNECTED.format(host=self.host, port=self.port))

            self._listener_thread = threading.Thread(target=self._listen_for_server_messages, daemon=True)
            self._listener_thread.start()

            self._send(f"{Q_CMD.REGISTER}{SEPARATOR}{self.name}")

            log(Fore.CYAN, MESSAGES.T.CLIENT, MESSAGES.CLIENT.IN_QUEUE_WAITING.format(name=self.name))

            while not self._is_active:
                if not self._is_connected:
                    raise ConnectionAbortedError(MESSAGES.CLIENT.CONNECTION_ABORTED_WHILE_WAITING)
                threading.Event().wait(timeout=0.1)

            log(Style.BRIGHT + Fore.GREEN, MESSAGES.T.CLIENT, MESSAGES.CLIENT.TURN_ARRIVED)

        except ConnectionRefusedError:
            log(Fore.RED, MESSAGES.T.CLIENT, MESSAGES.CLIENT.CONNECT_REFUSED)
            raise
        except Exception as e:
            log(Fore.RED, MESSAGES.T.CLIENT, MESSAGES.CLIENT.CONNECT_ERROR.format(error=e))
            self._is_connected = False
            if self._sock:
                self._sock.close()
            raise

    def _listen_for_server_messages(self):
        """Метод, который выполняется в фоновом потоке."""
        buffer = ""
        while self._is_connected:
            try:
                data = self._sock.recv(1024).decode('utf-8')
                if not data:
                    raise ConnectionAbortedError("Сервер разорвал соединение.")

                buffer += data
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    self._process_server_message(message.strip())

            except (ConnectionAbortedError, ConnectionResetError):
                if self._is_connected:
                    log(Fore.YELLOW, MESSAGES.T.CLIENT, MESSAGES.CLIENT.CONNECTION_LOST)
                self._is_connected = False
                self._response_event.set()
                self._is_active = True
                break
            except Exception:
                if self._is_connected:
                    log(Fore.RED, MESSAGES.T.CLIENT, MESSAGES.CLIENT.LISTENER_THREAD_ERROR)
                self._is_connected = False
                self._response_event.set()
                break

    def _process_server_message(self, message: str):
        """Обрабатывает одно сообщение от сервера."""
        if not message: return

        if message.startswith(Q_RSP.WELCOME_WAITING):
            parts = message.split(SEPARATOR)
            log(Fore.CYAN, MESSAGES.T.CLIENT, MESSAGES.CLIENT.QUEUE_POSITION_INFO.format(pos=parts[2], total=parts[3]))
            return

        parts = message.split(SEPARATOR)
        command = parts[0]
        params = parts[1:]

        if message == Q_RSP.WELCOME_ACTIVE or message == Q_RSP.PROMOTED:
            self._is_active = True
        elif command == Q_RSP.QUEUE_STATUS:
            log(Fore.CYAN, MESSAGES.T.CLIENT,
                MESSAGES.CLIENT.QUEUE_STATUS_UPDATE.format(pos=params[0], total=params[1]))
        elif command == Q_RSP.ERROR_NAME_TAKEN:
            log(Fore.RED, MESSAGES.T.CLIENT, MESSAGES.CLIENT.REG_NAME_TAKEN_ERROR)
            self._is_connected = False
            self._is_active = True
        elif command == Q_RSP.MANIPULATOR_RESPONSE:
            response_payload = SEPARATOR.join(params)
            with self._response_lock:
                self._last_response = response_payload
                self._response_event.set()

    def _send(self, command_str: str):
        if not self._is_connected:
            raise ConnectionError("Клиент не подключен к серверу.")
        self._sock.sendall((command_str + '\n').encode('utf-8'))

    def _send_command_and_wait_for_response(self, command_for_handler: str, timeout: float = 35.0) -> str:
        if not self._is_connected:
            raise ConnectionError("Клиент не подключен к серверу.")

        with self._response_lock:
            self._response_event.clear()
            self._last_response = ""

        full_command = f"{Q_CMD.MANIPULATOR}{SEPARATOR}{command_for_handler}"
        self._send(full_command)

        if self._response_event.wait(timeout):
            with self._response_lock:
                return self._last_response
        else:
            self.close()
            raise TimeoutError(f"Ответ от сервера не получен за {timeout} сек.")

    def close(self):
        if self._is_connected:
            self._is_connected = False
            if self._sock:
                try:
                    self._sock.shutdown(socket.SHUT_RDWR)
                    self._sock.close()
                except OSError:
                    pass
            log(Fore.CYAN, MESSAGES.T.CLIENT, MESSAGES.CLIENT.CONNECTION_CLOSED)
        if self._listener_thread and self._listener_thread.is_alive():
            self._listener_thread.join(timeout=1.0)


