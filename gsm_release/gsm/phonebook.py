
from core import GsmCore

class PhonebookMixin(GsmCore):
    def _read_phonebook(self):
        self._write("AT+CPBF=\"\"")
        return self.get_response(timeout_ms=2000).splitlines()
    def get_name(self, contact_no):
        for line in self._read_phonebook():
            if contact_no in line:
                parts = line.split(",")
                if len(parts) >= 4:
                    return parts[3].strip().strip('"')
        return ""
    def get_number(self, name):
        for line in self._read_phonebook():
            if name in line:
                parts = line.split(",")
                if len(parts) >= 2:
                    return parts[1].strip().strip('"')
        return ""
