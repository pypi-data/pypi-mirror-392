import socket
import threading
import time
from collections import deque
from colorama import Fore, Style

from dubina.utils import log
from dubina.locale.ru import MESSAGES
from dubina.remote.protocol import Q_CMD, Q_RSP, SEPARATOR
from .internal_api_server import InternalApiServer

HEARTBEAT_INTERVAL = 10  # Секунд


class Server:
    """
    Универсальный сервер, управляющий очередью клиентов к одному ресурсу (манипулятору).
    Может запускать внутренний API-сервер для вещания статуса.
    """

    def __init__(self, host, port, handler, internal_api_port=None):
        self.host = host
        self.port = port
        self.handler = handler
        self.internal_api_port = internal_api_port

        self._server_socket = None
        self._running = False

        self.client_queue = deque()
        self.active_clients = {}
        self.queue_lock = threading.Lock()
        self.all_threads = []

        self.internal_api = None

    def start(self):
        """Запускает сервер, начинает прослушивать порт и управлять очередью."""
        self._running = True

        # Запуск внутреннего API-сервера, если порт указан
        if self.internal_api_port:
            self.internal_api = InternalApiServer(host='127.0.0.1', port=self.internal_api_port)
            self.internal_api.start()
            self.all_threads.append(self.internal_api)

        queue_manager = QueueManager(self, interval=HEARTBEAT_INTERVAL)
        queue_manager.start()
        self.all_threads.append(queue_manager)

        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._server_socket.bind((self.host, self.port))
            self._server_socket.listen(5)
            ip_address = socket.gethostbyname(socket.gethostname())
            log(Fore.CYAN, MESSAGES.T.SERVER, MESSAGES.SERVER.STARTING.format(ip=ip_address, port=self.port))
        except OSError as e:
            log(Fore.RED, MESSAGES.T.SERVER, f"Не удалось запустить сервер: {e}")
            self._running = False
            return

        while self._running:
            try:
                conn, addr = self._server_socket.accept()
                handler_thread = ClientHandler(conn, addr, self)
                handler_thread.start()
                self.all_threads.append(handler_thread)
            except OSError:
                if self._running:
                    log(Fore.RED, MESSAGES.T.SERVER, MESSAGES.SERVER.CONNECTION_ERROR)
                break

        log(Fore.CYAN, MESSAGES.T.SERVER, MESSAGES.SERVER.CLEANUP)
        self._cleanup()

    def stop(self):
        """Корректно останавливает сервер и все дочерние потоки."""
        if self._running:
            self._running = False
            if self.internal_api:
                self.internal_api.stop()

            if self._server_socket:
                self._server_socket.close()
            log(Fore.CYAN, MESSAGES.T.SERVER, MESSAGES.SERVER.STOPPING)

    def _cleanup(self):
        """Очищает ресурсы и дожидается завершения потоков."""
        for thread in self.all_threads:
            if thread.is_alive():
                thread.join(timeout=1)
        log(Fore.CYAN, MESSAGES.T.SERVER, MESSAGES.SERVER.STOPPED)

    def remove_client(self, client_handler):
        """Потокобезопасное удаление клиента из всех структур."""
        client_was_in_queue = False
        with self.queue_lock:
            if client_handler.name in self.active_clients:
                del self.active_clients[client_handler.name]
            if client_handler in self.client_queue:
                self.client_queue.remove(client_handler)
                client_was_in_queue = True
                log(
                    Fore.YELLOW,
                    MESSAGES.T.QUEUE,
                    MESSAGES.QUEUE.CLIENT_REMOVED.format(name=client_handler.name, left=len(self.client_queue))
                )

        # Отправляем обновление очереди, если она изменилась
        if client_was_in_queue and self.internal_api:
            with self.queue_lock:
                queue_names = [client.name for client in self.client_queue]
            self.internal_api.send(f"QUEUE:{','.join(queue_names)}")


class ClientHandler(threading.Thread):
    """
    Поток, обрабатывающий одного подключенного клиента.
    """

    def __init__(self, sock, addr, server):
        super().__init__(daemon=True)
        self.sock = sock
        self.addr = addr
        self.server = server
        self.name = f"Unnamed-{addr[1]}"
        self._active_event = threading.Event()

    def run(self):
        log(Fore.GREEN, MESSAGES.T.CLIENT_HANDLER, MESSAGES.SERVER.CONNECTION_ACCEPTED.format(addr=self.addr))
        try:
            if not self._handle_registration():
                return

            self._active_event.wait()
            if not self.server._running: return

            log(Style.BRIGHT + Fore.GREEN, MESSAGES.T.CLIENT_HANDLER,
                MESSAGES.SERVER.CLIENT_PROMOTED.format(name=self.name))
            self._handle_active_session()

        except (ConnectionResetError, BrokenPipeError):
            log(Fore.YELLOW, MESSAGES.T.CLIENT_HANDLER,
                MESSAGES.SERVER.CLIENT_DISCONNECTED_UNEXPECTEDLY.format(name=self.name))
        except Exception as e:
            log(Fore.RED, MESSAGES.T.CLIENT_HANDLER, MESSAGES.SERVER.THREAD_ERROR.format(name=self.name, error=e))
        finally:
            self.server.remove_client(self)
            self.sock.close()
            log(
                Fore.CYAN,
                MESSAGES.T.CLIENT_HANDLER,
                MESSAGES.SERVER.CLIENT_DISCONNECTED_GRACEFULLY.format(addr=self.addr, name=self.name)
            )

    def _send(self, message):
        self.sock.sendall((message + '\n').encode('utf-8'))

    def _handle_registration(self):
        """Обрабатывает первое сообщение от клиента для регистрации в очереди."""
        try:
            self.sock.settimeout(5.0)
            data = self.sock.recv(1024).decode('utf-8').strip()
            self.sock.settimeout(None)

            if not data or not data.startswith(Q_CMD.REGISTER): return False

            self.name = data.split(SEPARATOR, 1)[1]

            with self.server.queue_lock:
                if self.name in self.server.active_clients:
                    log(Fore.YELLOW, MESSAGES.T.SERVER,
                        MESSAGES.SERVER.REG_NAME_TAKEN.format(addr=self.addr, name=self.name))
                    self._send(Q_RSP.ERROR_NAME_TAKEN)
                    return False

                self.server.active_clients[self.name] = self
                self.server.client_queue.append(self)
                pos = len(self.server.client_queue)
                log(Fore.CYAN, MESSAGES.T.QUEUE, MESSAGES.QUEUE.CLIENT_ADDED.format(name=self.name, pos=pos))

                # Отправляем обновление очереди во внутренний API
                if self.server.internal_api:
                    queue_names = [client.name for client in self.server.client_queue]
                    self.server.internal_api.send(f"QUEUE:{','.join(queue_names)}")

                if pos == 1:
                    self.set_active()
                    self._send(Q_RSP.WELCOME_ACTIVE)
                else:
                    total = len(self.server.client_queue)
                    self._send(f"{Q_RSP.WELCOME_WAITING}{SEPARATOR}{pos}{SEPARATOR}{total}")
            return True
        except socket.timeout:
            log(Fore.YELLOW, MESSAGES.T.SERVER, MESSAGES.SERVER.REG_TIMEOUT.format(addr=self.addr))
            return False
        except (IndexError, UnicodeDecodeError):
            log(Fore.YELLOW, MESSAGES.T.SERVER, MESSAGES.SERVER.REG_INVALID.format(addr=self.addr))
            return False

    def _handle_active_session(self):
        """Цикл обработки команд от клиента, когда его очередь подошла."""
        while self.server._running:
            data = self.sock.recv(1024).decode('utf-8').strip()
            if not data: break

            if not data.startswith(Q_CMD.MANIPULATOR):
                log(Fore.YELLOW, MESSAGES.T.CLIENT_HANDLER,
                    MESSAGES.SERVER.CMD_INVALID.format(name=self.name, data=data))
                continue

            command_for_handler = data.split(SEPARATOR, 1)[1]
            log(Fore.CYAN, MESSAGES.T.SERVER,
                MESSAGES.SERVER.CMD_RECEIVED.format(name=self.name, command=command_for_handler))

            # Передаем internal_api в обработчик, чтобы он мог слать логи о статусе команды
            response_from_handler = self.server.handler.process_command(
                command_str=command_for_handler,
                user_name=self.name,
                internal_api=self.server.internal_api
            )

            log(Fore.GREEN, MESSAGES.T.SERVER,
                MESSAGES.SERVER.CMD_RESPONSE.format(name=self.name, response=response_from_handler))
            self._send(f"{Q_RSP.MANIPULATOR_RESPONSE}{SEPARATOR}{response_from_handler}")

    def set_active(self):
        """Активирует клиента, позволяя ему выйти из ожидания."""
        self._active_event.set()


class QueueManager(threading.Thread):
    """
    Фоновый поток, который следит за очередью.
    """

    def __init__(self, server, interval):
        super().__init__(daemon=True)
        self.server = server
        self.interval = interval

    def run(self):
        while self.server._running:
            time.sleep(self.interval)

            clients_to_remove = []

            with self.server.queue_lock:
                if not self.server.client_queue: continue

                active_client = self.server.client_queue[0]
                if not active_client._active_event.is_set():
                    active_client.set_active()
                    try:
                        active_client._send(Q_RSP.PROMOTED)
                    except (ConnectionResetError, BrokenPipeError):
                        clients_to_remove.append(active_client)

                waiting_clients = list(self.server.client_queue)[1:]
                for i, client in enumerate(waiting_clients):
                    pos = i + 2
                    total = len(self.server.client_queue)
                    status_msg = f"{Q_RSP.QUEUE_STATUS}{SEPARATOR}{pos}{SEPARATOR}{total}"
                    try:
                        client._send(status_msg)
                    except (ConnectionResetError, BrokenPipeError):
                        log(Fore.YELLOW, MESSAGES.T.QUEUE, MESSAGES.QUEUE.HEARTBEAT_FAILED.format(name=client.name))
                        clients_to_remove.append(client)

            if clients_to_remove:
                for client in clients_to_remove:
                    self.server.remove_client(client)
