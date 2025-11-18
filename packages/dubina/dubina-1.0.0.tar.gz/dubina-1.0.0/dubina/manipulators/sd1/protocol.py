# ==============================================================================
# ПРОТОКОЛ "УМНЫЙ МОСТ" v4.0 (Обработчик SD1_Handler <-> Arduino)
# ==============================================================================

# Этот файл содержит константы для бинарного протокола общения
# с прошивкой манипулятора SD1.

START_BYTE = 0xAA

CMD = {
    "PING": 0x01,
    "CALIBRATE": 0x02,
    "SET_MAX_SPEED": 0x03,
    "SET_ACCELERATION": 0x04,
    "SET_TOOL_OFFSET": 0x05,
    "MOVE_TO": 0x10,
    "MOVE_RELATIVE": 0x11,
    "JUMP_TO": 0x12,
    "J_MOVE_TO": 0x18,
    "J_MOVE_RELATIVE": 0x19,
    "TOOL_VACUUM": 0x20,
    "TOOL_ROTATE_TO": 0x22,
    "GET_POSITION": 0x30,
    "J_GET_POSITION": 0x31,
    "GET_FIRMWARE_VERSION": 0x32
}

RSP = {
    0x80: "ACK",
    0x81: "PONG",
    0x82: "ERROR",
    0x90: "POSITION",
    0x91: "J_POSITION",
    0x92: "FIRMWARE"
}

ERR = {
    0x01: "UNKNOWN_COMMAND",
    0x02: "BAD_CHECKSUM",
    0x04: "STM32_TIMEOUT",
    0x0F: "MOVE_FAILED"  # Универсальная ошибка: движение не удалось
}