# example_sta.py
# ─────────────────────────────────────────────────────────────────────────────
# WebFileManager — Station (STA) mode example
# Connect your MicroPython device to an existing WiFi router.
# ─────────────────────────────────────────────────────────────────────────────
#
# File layout on your device:
#
#   /                          <- device root
#   ├── example_sta.py         <- this file (rename to main.py to auto-run)
#   └── WebFileManager/        <- the library folder
#       ├── __init__.py
#       ├── server.py
#       ├── http.py
#       ├── upload.py
#       ├── ui.py
#       ├── fileops.py
#       ├── wifi.py
#       └── utils.py
#
# Flash this with mpremote, Thonny, rshell, or ampy.
# ─────────────────────────────────────────────────────────────────────────────

import WebFileManager

WebFileManager.start(
    ssid     = "YourWiFiSSID",       # <-- change this
    password = "YourWiFiPassword",   # <-- change this
    port     = 8080,
    root     = "/",
)

# Open your browser and visit:  http://<device-ip>:8080/
