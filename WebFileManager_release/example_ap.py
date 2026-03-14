# example_ap.py
# ─────────────────────────────────────────────────────────────────────────────
# WebFileManager — Access Point (AP) mode example
# The device creates its own WiFi hotspot — no router required.
# Great for field use or initial setup.
# ─────────────────────────────────────────────────────────────────────────────

import WebFileManager

WebFileManager.start(
    ap_mode  = True,
    ap_ssid  = "ESP32-Files",   # hotspot name your phone/laptop will see
    ap_pass  = "micropython",   # hotspot password (min 8 chars for WPA2)
                                # set ap_pass='' for an open / no-password AP
    port     = 80,
    root     = "/",
)

# 1. On your phone or laptop, connect to the "ESP32-Files" WiFi network.
# 2. Open your browser and go to:  http://192.168.4.1/
