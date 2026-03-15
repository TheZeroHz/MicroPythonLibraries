
from core import GsmCore

class SmsMixin(GsmCore):
    def msg(self, number, text):
        self._write("AT+CMGF=1")
        self.get_response()
        self._write("AT+CNMI=1,2,0,0,0")
        self.get_response()
        self._write_raw(("AT+CMGS=\"" + number + "\"\r").encode())
        self.get_response()
        self._write_raw((text + "\x1a").encode())
        print(self.get_response(timeout_ms=5000))
