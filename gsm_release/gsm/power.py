
import time
from core import GsmCore

class PowerMixin(GsmCore):
    def is_ok(self):
        self._write("AT")
        return "OK" in self.get_response()
    def battery_percentage(self):
        self._write("AT+CBC")
        response = self.get_response()
        try:
            i = response.index(",")
            j = response.index(",", i + 1)
            return int(response[i+1:j])
        except:
            return -1
    def deep_sleep(self):
        self._write("AT+CSCLK=2")
    def wake_up(self):
        self._write_raw(b"\r")
        time.sleep_ms(500)
        self._write("AT+CSCLK=0")
        self.get_response()
