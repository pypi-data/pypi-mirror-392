import threading
import time
import struct
import serial
import serial.tools.list_ports
from colorama import Fore, Style

from dubina.utils import log
from dubina.locale.ru import MESSAGES
from dubina.manipulators.sd1.protocol import START_BYTE, CMD, RSP, ERR


class SD1_Handler:
    def __init__(self):
        self.ser = None
        self.serial_lock = threading.Lock()
        self._find_and_connect_to_arduino()

    def _find_and_connect_to_arduino(self):
        log(Fore.CYAN, MESSAGES.T.SD1_HANDLER, MESSAGES.SD1.SEARCHING)
        ports = serial.tools.list_ports.comports()
        if not ports:
            raise ConnectionError(MESSAGES.SD1.SEARCH_NO_PORTS)

        for p in ports:
            try:
                ser = serial.Serial(p.device, 115200, timeout=2)

                is_ready = False
                start_wait = time.time()
                while time.time() - start_wait < 3.0:
                    self._send_packet_to_arduino(ser, CMD["PING"])
                    rsp_id, _ = self._read_packet_from_arduino(ser, timeout=1)

                    if rsp_id is not None and RSP.get(rsp_id) == "PONG":
                        log(
                            Style.BRIGHT + Fore.GREEN,
                            MESSAGES.T.SD1_HANDLER,
                            MESSAGES.SD1.FOUND_AND_READY.format(device=p.device)
                        )
                        self.ser = ser
                        is_ready = True
                        break

                if is_ready:
                    return
                else:
                    ser.close()
            except serial.SerialException:
                log(Fore.YELLOW, MESSAGES.T.SD1_HANDLER, MESSAGES.SD1.SEARCH_PORT_BUSY.format(device=p.device))
                continue
            except Exception as e:
                log(Fore.RED, MESSAGES.T.SD1_HANDLER, MESSAGES.SD1.SEARCH_PORT_ERROR.format(device=p.device, error=e))
                if 'ser' in locals() and ser.is_open:
                    ser.close()
                continue

        raise ConnectionError(MESSAGES.SD1.SEARCH_FAILED_FINAL)

    # --- ИЗМЕНЕНИЕ: Новая сигнатура метода ---
    def process_command(self, command_str: str, user_name: str, internal_api) -> str:
        """
        Главный метод, который вызывает универсальный сервер.
        """
        parts = command_str.split()
        cmd_name = parts[0]
        args = parts[1:]

        if cmd_name not in CMD:
            return f"ERROR: Unknown command '{cmd_name}'"

        # --- ОТПРАВКА ЛОГА О НАЧАЛЕ КОМАНДЫ ---
        if internal_api:
            # Отправляем только имя команды, без аргументов
            internal_api.send(f"LOG:{user_name}:{cmd_name}:START")

        cmd_id = CMD[cmd_name]
        payload = b''

        try:
            if cmd_name in ["SET_MAX_SPEED", "SET_ACCELERATION", "MOVE_TO", "MOVE_RELATIVE", "JUMP_TO"]:
                payload = struct.pack('<hhh', *[int(v) for v in args])
            elif cmd_name in ["SET_TOOL_OFFSET", "J_MOVE_TO", "J_MOVE_RELATIVE"]:
                payload = struct.pack('<fff', *[float(v) for v in args])
            elif cmd_name == "TOOL_VACUUM":
                payload = struct.pack('<B', int(args[0]))
            elif cmd_name == "TOOL_ROTATE_TO":
                payload = struct.pack('<B', int(args[0]))
        except (ValueError, IndexError):
            if internal_api:
                internal_api.send(f"LOG:{user_name}:{cmd_name}:ERROR")
            return "ERROR: Invalid arguments for command"

        with self.serial_lock:
            self._send_packet_to_arduino(self.ser, cmd_id, payload)
            rsp_id, rsp_payload = self._read_packet_from_arduino(self.ser, timeout=30)

        # --- ОТПРАВКА ЛОГА О РЕЗУЛЬТАТЕ КОМАНДЫ ---
        if internal_api:
            if rsp_id is not None and RSP.get(rsp_id) not in ["ERROR"]:
                status = "OK"
            else:
                status = "ERROR"
            internal_api.send(f"LOG:{user_name}:{cmd_name}:{status}")

        if rsp_id is None:
            return "ERROR: No response from Arduino (Timeout)"

        response_type = RSP.get(rsp_id)
        if response_type in ["ACK", "PONG"]:
            return response_type
        elif response_type == "ERROR":
            error_code = rsp_payload[0]
            error_name = ERR.get(error_code, "UNKNOWN_ERROR_CODE")
            return f"ERROR: {error_name} (Code: 0x{error_code:02X})"
        elif response_type == "POSITION":
            x, y, z = struct.unpack('<hhh', rsp_payload)
            return f"POSITION {x} {y} {z}"
        elif response_type == "J_POSITION":
            j1, j2, j3 = struct.unpack('<fff', rsp_payload)
            return f"J_POSITION {j1:.2f} {j2:.2f} {j3:.2f}"
        elif response_type == "FIRMWARE":
            v = struct.unpack('<BBBB', rsp_payload)
            return f"FIRMWARE {v[0]}.{v[1]}.{v[2]}.{v[3]}"
        else:
            return "ERROR: Received unknown response ID"

    def _pack_packet(self, cmd_id, payload=b''):
        payload_len = len(payload)
        header = struct.pack('<BBB', START_BYTE, cmd_id, payload_len)
        packet_without_checksum = header + payload
        checksum = 0
        for byte in packet_without_checksum:
            checksum ^= byte
        return packet_without_checksum + struct.pack('<B', checksum)

    def _send_packet_to_arduino(self, ser, cmd_id, payload=b''):
        ser.reset_output_buffer()
        packet = self._pack_packet(cmd_id, payload)
        ser.write(packet)
        ser.flush()

    def _read_packet_from_arduino(self, ser, timeout=15):
        ser.reset_input_buffer()
        start_time = time.time()
        while time.time() - start_time < timeout:
            if ser.in_waiting > 0 and ser.read(1) == bytes([START_BYTE]):
                header_bytes = ser.read(2)
                if len(header_bytes) < 2: continue

                rsp_id, payload_len = struct.unpack('<BB', header_bytes)

                full_payload_time = time.time()
                while ser.in_waiting < payload_len + 1:
                    time.sleep(0.001)
                    if time.time() - full_payload_time > 2:
                        return None, None

                payload = ser.read(payload_len)
                checksum_byte = ser.read(1)

                if len(payload) < payload_len or len(checksum_byte) < 1: continue

                received_checksum = checksum_byte[0]
                calculated_checksum = START_BYTE ^ rsp_id ^ payload_len
                for byte in payload:
                    calculated_checksum ^= byte

                if calculated_checksum == received_checksum:
                    return rsp_id, payload
                else:
                    return RSP.get("ERROR"), struct.pack('<B', ERR.get("BAD_CHECKSUM"))
        return None, None
