from colorama import Fore

from dubina.remote.server import Server as UniversalServer
from dubina.manipulators.sd1.server_handler import SD1_Handler
from dubina.utils import log
from dubina.locale.ru import MESSAGES

SUPPORTED_MANIPULATORS = {
    "sd1": SD1_Handler,
}

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 5000


def create_server(manipulator_type: str,
                  host: str = DEFAULT_HOST,
                  port: int = DEFAULT_PORT,
                  internal_port: int = None):
    """
    Фабричная функция для создания и настройки сервера под конкретный манипулятор.

    Args:
        manipulator_type (str): Строковой идентификатор манипулятора.
        host (str, optional): IP-адрес для прослушивания. По умолчанию '0.0.0.0'.
        port (int, optional): Порт для прослушивания. По умолчанию 5000.
        internal_port (int, optional): Порт для внутреннего API. Если указан,
                                       сервер будет вещать свой статус. По умолчанию None.
    """
    manipulator_type = manipulator_type.lower()
    HandlerClass = SUPPORTED_MANIPULATORS.get(manipulator_type)

    if not HandlerClass:
        supported_list = list(SUPPORTED_MANIPULATORS.keys())
        error_msg = MESSAGES.FACTORY.UNKNOWN_MANIPULATOR_ERROR.format(
            type=manipulator_type,
            supported_list=supported_list
        )
        log(Fore.RED, MESSAGES.T.FACTORY, error_msg)
        raise ValueError(error_msg)

    log(Fore.CYAN, MESSAGES.T.FACTORY, MESSAGES.FACTORY.INIT_HANDLER.format(type=manipulator_type))
    try:
        handler = HandlerClass()
        log(Fore.GREEN, MESSAGES.T.FACTORY, MESSAGES.FACTORY.INIT_HANDLER_SUCCESS.format(type=manipulator_type))
    except Exception as e:
        log(Fore.RED, MESSAGES.T.FATAL, MESSAGES.FACTORY.INIT_HANDLER_ERROR.format(type=manipulator_type, error=e))
        raise

    log(Fore.CYAN, MESSAGES.T.FACTORY, MESSAGES.FACTORY.CREATING_SERVER)

    server_instance = UniversalServer(
        host=host,
        port=port,
        handler=handler,
        internal_api_port=internal_port
    )

    return server_instance
