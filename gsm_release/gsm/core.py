"""
gsm/core.py
-----------
Low-level UART transport for GSM modules.
All higher-level modules inherit from GsmCore.
"""

import time
from machine import UART, Pin


class GsmCore:
    """
    Handles raw UART communication with the GSM module.
    Not intended to be used directly — use the Phone facade instead.
    """

    def __init__(self, uart_id: int, tx_pin: int, rx_pin: int, baud: int) -> None:
        self._uart = UART(
            uart_id,
            baudrate=baud,
            tx=Pin(tx_pin),
            rx=Pin(rx_pin),
            bits=8,
            parity=None,
            stop=1,
        )

    # ------------------------------------------------------------------
    # Transport primitives
    # ------------------------------------------------------------------

    def _write(self, text: str) -> None:
        """Send *text* terminated with CR+LF."""
        self._uart.write((text + "\r\n").encode())

    def _write_raw(self, data: bytes) -> None:
        """Send raw bytes without any terminator."""
        self._uart.write(data)

    def get_response(self, timeout_ms: int = 1000) -> str:
        """
        Collect all bytes arriving within *timeout_ms* milliseconds.

        :param timeout_ms: Read window in ms (default 1000).
        :return: Decoded, stripped response string.
        """
        buf = b""
        start = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start) < timeout_ms:
            if self._uart.any():
                chunk = self._uart.read(self._uart.any())
                if chunk:
                    buf += chunk
            time.sleep_ms(10)
        return buf.decode("utf-8", "ignore").strip()

    def cmd(self, command: str, timeout_ms: int = 1000) -> str:
        """
        Send an AT command and return the response string.

        :param command:    AT command (e.g. ``'AT+CSQ'``).
        :param timeout_ms: Response timeout in ms.
        :return: Module response.
        """
        self._write(command)
        response = self.get_response(timeout_ms)
        print(response)
        return response

