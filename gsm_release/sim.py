"""
examples/basic_usage.py
-----------------------
Basic connectivity check, battery level, and time query.
Copy this file and gsm/ to your Pico with mpremote or Thonny.
"""

from gsm import Phone

# Adjust pins to match your wiring
gsm = Phone(uart_id=1, tx_pin=4, rx_pin=5, baud=9600)

if gsm.is_ok():
    print("GSM module is online.")
    print("Battery:", gsm.battery_percentage(), "%")
    print("Date   :", gsm.get_date())
    print("Time   :", gsm.get_time())
    number = "+8801974682349"  # Replace with your number
    print(f"Calling {number}...")
    gsm.call(number)
    # Let it ring for 20 seconds, then hang up
    import time
    time.sleep(20)
    gsm.cut_call()
    print("Call ended.")
else:
    print("GSM module not responding. Check wiring and baud rate.")

