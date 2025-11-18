# ==============================================================================
# Файл локализации для библиотеки 'dubina'. Версия: ru (Русский)
# ==============================================================================
# Этот файл содержит все строки, выводимые пользователю.
# {переменная} - это плейсхолдер для форматирования строк.
# ==============================================================================

class LOG_LEVELS:
    SERVER = "[SERVER]"
    FACTORY = "[FACTORY]"
    QUEUE = "[QUEUE]"
    CLIENT_HANDLER = "[CLIENT-HANDLER]"
    SD1_HANDLER = "[SD1-HANDLER]"
    CLIENT = "[CLIENT]"
    MAIN = "[MAIN]"
    FATAL = "[FATAL]"
    INTERNAL_API = "[INTERNAL-API]"
    WEB = "[WEB-SERVER]"


class SERVER_MESSAGES:
    STARTING = "Сервер запущен на {ip}:{port}, ожидаем клиентов..."
    STOPPING = "Инициирована остановка сервера."
    STOPPED = "Сервер завершил работу."
    CLEANUP = "Сервер останавливается..."
    CONNECTION_ACCEPTED = "Новое подключение от {addr}"
    CONNECTION_ERROR = "Ошибка при приеме соединения."

    REG_TIMEOUT = "Клиент {addr} не зарегистрировался вовремя. Отключение."
    REG_INVALID = "Некорректное сообщение о регистрации от {addr}."
    REG_NAME_TAKEN = "Клиенту {addr} отказано: имя '{name}' уже занято."

    CMD_RECEIVED = "'{name}' -> HANDLER: '{command}'"
    CMD_RESPONSE = "HANDLER -> '{name}': '{response}'"
    CMD_INVALID = "Получена некорректная команда от '{name}': {data}"

    CLIENT_DISCONNECTED_UNEXPECTEDLY = "Клиент '{name}' разорвал соединение."
    CLIENT_DISCONNECTED_GRACEFULLY = "Соединение с {addr} ('{name}') закрыто."
    THREAD_ERROR = "Ошибка в потоке для '{name}': {error}"

    CLIENT_PROMOTED = "Клиент '{name}' получил управление."


class CLIENT_MESSAGES:
    CONNECTED = "Успешно подключено к серверу {host}:{port}"
    CONNECT_REFUSED = "Не удалось подключиться: сервер отклонил соединение."
    CONNECT_ERROR = "Произошла ошибка при подключении: {error}"

    IN_QUEUE_WAITING = "{name}, вы добавлены в очередь. Ожидаем..."
    QUEUE_STATUS_UPDATE = "Статус очереди. Ваша позиция: {pos} из {total}."
    QUEUE_POSITION_INFO = "Вы в очереди. Позиция: {pos} из {total}."

    TURN_ARRIVED = "Ваша очередь подошла! Управление передано."

    REG_NAME_TAKEN_ERROR = "Ошибка регистрации: это имя уже используется."

    CMD_TIMEOUT_ERROR = "Ошибка: Таймаут ожидания ответа от сервера на команду '{command}'."
    CMD_EXECUTION_ERROR = "Ошибка выполнения команды '{command}': {response}"
    CMD_CRITICAL_ERROR = "Критическая ошибка при выполнении команды '{command}': {error}"

    VALIDATION_ANGLE_ERROR = "Ошибка: Угол {angle} выходит за пределы ({min_angle}, {max_angle})"

    CONNECTION_LOST = "Соединение с сервером потеряно."
    CONNECTION_CLOSED = "Соединение с сервером закрыто."
    CONNECTION_ABORTED_WHILE_WAITING = "Соединение было разорвано во время ожидания в очереди."
    LISTENER_THREAD_ERROR = "Критическая ошибка в потоке-слушателе."


class QUEUE_MESSAGES:
    CLIENT_ADDED = "Клиент '{name}' добавлен в очередь на позицию {pos}."
    CLIENT_REMOVED = "Клиент '{name}' удален из очереди. Осталось в очереди: {left}."
    HEARTBEAT_FAILED = "Heartbeat для '{name}' не удался. Помечен на удаление."


class SD1_HANDLER_MESSAGES:
    SEARCHING = "Поиск Arduino на COM-портах..."
    SEARCH_NO_PORTS = "Не найдено ни одного COM-порта."
    SEARCH_PORT_BUSY = "Порт {device} занят или не отвечает."
    SEARCH_PORT_ERROR = "Неожиданная ошибка на порту {device}: {error}"
    SEARCH_FAILED_FINAL = "Не удалось найти Arduino. Проверьте подключение, драйверы и прошивку."
    FOUND_AND_READY = "Arduino найдена и готова к работе на порту {device}"


class FACTORY_MESSAGES:
    INIT_HANDLER = "Инициализация обработчика для '{type}'..."
    INIT_HANDLER_SUCCESS = "Обработчик '{type}' успешно инициализирован."
    INIT_HANDLER_ERROR = "Ошибка при инициализации обработчика '{type}': {error}"
    CREATING_SERVER = "Создание экземпляра универсального сервера..."
    UNKNOWN_MANIPULATOR_ERROR = ("Неизвестный тип манипулятора: '{type}'. "
                                 "Поддерживаются: {supported_list}")


class MAIN_SCRIPT_MESSAGES:
    STARTING_SERVER = "Попытка запуска сервера для манипулятора '{type}'..."
    SERVER_CREATE_ERROR = "Не удалось создать сервер: {error}"
    KEYBOARD_INTERRUPT = "\nПолучен сигнал прерывания (Ctrl+C). Остановка сервера..."
    UNEXPECTED_SERVER_ERROR = "Произошла непредвиденная ошибка сервера: {error}"
    PROGRAM_FINISHED = "Программа завершена."


class WEB_SERVER_MESSAGES:
    BROWSER_CONNECTED = "Браузер подключился по WebSocket."
    UDP_LISTENER_STARTED = "UDP-слушатель запущен на {host}:{port}"
    TCP_LISTENER_STARTED = "Клиент внутреннего API запущен, подключаемся к {host}:{port}..."
    TCP_LISTENER_ERROR = "Не удалось запустить клиент внутреннего API: {error}"
    TCP_CONNECTION_SUCCESS = "Успешно подключено к серверу манипулятора."
    TCP_CONNECTION_LOST = "Соединение с сервером манипулятора потеряно. Попытка переподключения..."
    TCP_CONNECTION_ERROR = "Ошибка клиента внутреннего API: {error}"
    STARTING = "Веб-сервер запущен. Откройте http://{host}:{port} в браузере."
    START_ERROR = "Не удалось запустить веб-сервер: {error}"
    STOPPING = "Веб-сервер останавливается."


# Главный "контейнер" для всех сообщений для удобного импорта.
class RU:
    T = LOG_LEVELS
    SERVER = SERVER_MESSAGES
    CLIENT = CLIENT_MESSAGES
    QUEUE = QUEUE_MESSAGES
    SD1 = SD1_HANDLER_MESSAGES
    FACTORY = FACTORY_MESSAGES
    MAIN = MAIN_SCRIPT_MESSAGES
    WEB = WEB_SERVER_MESSAGES


# Создаем один экземпляр, который будет импортироваться везде.
MESSAGES = RU()
