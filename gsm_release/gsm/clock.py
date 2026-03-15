
from core import GsmCore

class ClockMixin(GsmCore):
    def _query_clock(self):
        self._write("AT+CCLK?")
        return self.get_response()
    def get_time(self):
        response = self._query_clock()
        try:
            comma = response.index(",")
            t = response[comma+1:].strip().strip('"')
            for sep in ("+", "-"):
                idx = t.rfind(sep)
                if idx > 0:
                    t = t[:idx]
            return t
        except:
            return ""
    def get_date(self):
        response = self._query_clock()
        try:
            start = response.index('"') + 1
            comma = response.index(",")
            return response[start:comma]
        except:
            return ""
