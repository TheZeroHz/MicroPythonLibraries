import sys
_pkg = __file__.rsplit('/', 1)[0]
if _pkg not in sys.path:
    sys.path.insert(0, _pkg)

from core import GsmCore
from call import CallMixin
from sms import SmsMixin
from phonebook import PhonebookMixin
from power import PowerMixin
from clock import ClockMixin

class Phone(CallMixin, SmsMixin, PhonebookMixin, PowerMixin, ClockMixin):
    def __init__(self, uart_id=1, tx_pin=4, rx_pin=5, baud=9600):
        super().__init__(uart_id=uart_id, tx_pin=tx_pin, rx_pin=rx_pin, baud=baud)
