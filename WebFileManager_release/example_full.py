# example_full.py
# ─────────────────────────────────────────────────────────────────────────────
# WebFileManager — all options example
# HTTP Basic Auth + custom root + custom port
# ─────────────────────────────────────────────────────────────────────────────

import WebFileManager

WebFileManager.start(
    # ── WiFi (STA mode) ────────────────────────────────────────────────────
    ssid      = "YourWiFiSSID",
    password  = "YourWiFiPassword",
    timeout   = 30,            # seconds to wait for WiFi before raising OSError

    # ── HTTP server ─────────────────────────────────────────────────────────
    port      = 80,            # use 80 so you don't need :port in the URL
    root      = "/sd",         # expose only the SD card, not internal flash

    # ── HTTP Basic Auth ─────────────────────────────────────────────────────
    # Leave http_user='' to disable auth (anyone on the network can connect).
    http_user = "admin",
    http_pass = "admin",
)

# Visit:  http://<device-ip>/
# Browser will prompt for username/password.
