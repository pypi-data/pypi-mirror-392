from typing import Tuple, Union
from colorama import Fore

from dubina.remote.client_base import BaseClient
from dubina.utils import log
from dubina.locale.ru import MESSAGES


class Client(BaseClient):
    """
    Клиентский класс для управления манипулятором SD1 через сервер.
    """
    MIN_TOOL_ANGLE = 0
    MAX_TOOL_ANGLE = 180

    def __init__(self, host: str, port: int, name: str, debug: bool = False):
        """
        Инициализирует клиент, подключается к серверу и ждет своей очереди.

        Args:
            host (str): IP-адрес сервера.
            port (int): Порт сервера.
            name (str): Уникальное имя клиента для очереди.
            debug (bool, optional): Включает подробное логирование команд. По умолчанию False.
        """
        super().__init__(host, port, name)
        self.debug = debug
        self.current_tool_angle = 90

    def _execute_and_check(self, command_str: str) -> bool:
        """Внутренний метод для отправки команды и проверки ответа 'ACK'."""
        if self.debug:
            log(Fore.YELLOW, MESSAGES.T.CLIENT, f"Отправка: {command_str}")
        try:
            response = self._send_command_and_wait_for_response(command_str)
            if response == "ACK":
                if self.debug:
                    log(Fore.GREEN, MESSAGES.T.CLIENT, f"Ответ на '{command_str}': Успешно (ACK)")
                return True
            else:
                log(Fore.RED, MESSAGES.T.CLIENT,
                    MESSAGES.CLIENT.CMD_EXECUTION_ERROR.format(command=command_str, response=response))
                return False
        except TimeoutError:
            log(Fore.RED, MESSAGES.T.CLIENT, MESSAGES.CLIENT.CMD_TIMEOUT_ERROR.format(command=command_str))
            return False
        except Exception as e:
            log(Fore.RED, MESSAGES.T.CLIENT, MESSAGES.CLIENT.CMD_CRITICAL_ERROR.format(command=command_str, error=e))
            return False

    # --- Публичные методы ---

    def move_to(self, x: int, y: int, z: int) -> bool:
        return self._execute_and_check(f"MOVE_TO {int(x)} {int(y)} {int(z)}")

    def move_relative(self, dx: int, dy: int, dz: int) -> bool:
        return self._execute_and_check(f"MOVE_RELATIVE {int(dx)} {int(dy)} {int(dz)}")

    def jump_to(self, x: int, y: int, delta_z: int) -> bool:
        return self._execute_and_check(f"JUMP_TO {int(x)} {int(y)} {int(delta_z)}")

    def calibrate(self) -> bool:
        return self._execute_and_check("CALIBRATE")

    def set_max_speed(self, sx: int, sy: int, sz: int) -> bool:
        return self._execute_and_check(f"SET_MAX_SPEED {int(sx)} {int(sy)} {int(sz)}")

    def set_acceleration(self, ax: int, ay: int, az: int) -> bool:
        return self._execute_and_check(f"SET_ACCELERATION {int(ax)} {int(ay)} {int(az)}")

    def set_tool_offset(self, tx: float, ty: float, tz: float) -> bool:
        return self._execute_and_check(f"SET_TOOL_OFFSET {tx} {ty} {tz}")

    def j_move_to(self, j1: float, j2: float, j3: float) -> bool:
        return self._execute_and_check(f"J_MOVE_TO {j1} {j2} {j3}")

    def j_move_relative(self, dj1: float, dj2: float, dj3: float) -> bool:
        return self._execute_and_check(f"J_MOVE_RELATIVE {dj1} {dj2} {dj3}")

    def vacuum(self, state: bool) -> bool:
        return self._execute_and_check(f"TOOL_VACUUM {1 if state else 0}")

    def rotate_to(self, angle: int) -> bool:
        angle = int(angle)
        if not (self.MIN_TOOL_ANGLE <= angle <= self.MAX_TOOL_ANGLE):
            log(
                Fore.RED,
                MESSAGES.T.CLIENT,
                MESSAGES.CLIENT.VALIDATION_ANGLE_ERROR.format(angle=angle, min_angle=self.MIN_TOOL_ANGLE,
                                                              max_angle=self.MAX_TOOL_ANGLE)
            )
            return False

        success = self._execute_and_check(f"TOOL_ROTATE_TO {angle}")
        if success:
            self.current_tool_angle = angle
        return success

    # --- Методы для получения информации ---

    def get_position(self) -> Union[Tuple[int, int, int], None]:
        command_str = "GET_POSITION"
        if self.debug:
            log(Fore.CYAN, MESSAGES.T.CLIENT, f"Запрос: {command_str}")
        try:
            response = self._send_command_and_wait_for_response(command_str)
            if response.startswith("POSITION"):
                parts = response.split()
                coords = tuple(map(int, parts[1:]))
                if self.debug:
                    log(Fore.GREEN, MESSAGES.T.CLIENT, f"Ответ: Текущие координаты {coords}")
                return coords
            else:
                log(Fore.RED, MESSAGES.T.CLIENT,
                    MESSAGES.CLIENT.CMD_EXECUTION_ERROR.format(command=command_str, response=response))
                return None
        except Exception as e:
            log(Fore.RED, MESSAGES.T.CLIENT, MESSAGES.CLIENT.CMD_CRITICAL_ERROR.format(command=command_str, error=e))
            return None

    def get_joint_position(self) -> Union[Tuple[float, float, float], None]:
        command_str = "J_GET_POSITION"
        if self.debug:
            log(Fore.CYAN, MESSAGES.T.CLIENT, f"Запрос: {command_str}")
        try:
            response = self._send_command_and_wait_for_response(command_str)
            if response.startswith("J_POSITION"):
                parts = response.split()
                coords = tuple(map(float, parts[1:]))
                if self.debug:
                    log(Fore.GREEN, MESSAGES.T.CLIENT, f"Ответ: Текущие углы сочленений {coords}")
                return coords
            else:
                log(Fore.RED, MESSAGES.T.CLIENT,
                    MESSAGES.CLIENT.CMD_EXECUTION_ERROR.format(command=command_str, response=response))
                return None
        except Exception as e:
            log(Fore.RED, MESSAGES.T.CLIENT, MESSAGES.CLIENT.CMD_CRITICAL_ERROR.format(command=command_str, error=e))
            return None

    def get_firmware_version(self) -> Union[str, None]:
        command_str = "GET_FIRMWARE_VERSION"
        if self.debug:
            log(Fore.CYAN, MESSAGES.T.CLIENT, f"Запрос: {command_str}")
        try:
            response = self._send_command_and_wait_for_response(command_str)
            if self.debug:
                log(Fore.GREEN, MESSAGES.T.CLIENT, f"Ответ: {response}")
            return response
        except Exception as e:
            log(Fore.RED, MESSAGES.T.CLIENT, MESSAGES.CLIENT.CMD_CRITICAL_ERROR.format(command=command_str, error=e))
            return None


