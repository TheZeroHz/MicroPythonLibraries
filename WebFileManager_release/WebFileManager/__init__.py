"""
WebFileManager — MicroPython Web File Manager
==============================================
A modular, browser-based file manager for ESP32, ESP32-S3, RP2040-W
and other MicroPython devices.

Author  : Rakib Hasan (@thezerohz) — https://github.com/thezerohz
License : MIT

Usage — importable as a package from a folder
----------------------------------------------
    # Copy the entire WebFileManager/ folder next to your main.py
    # (or into /lib/ on your device), then:

    import WebFileManager
    WebFileManager.start(ssid="MyWifi", password="secret")

    # — or —
    from WebFileManager import start
    start(ap_mode=True, ap_ssid="PicoAP")

Module layout (inside the WebFileManager/ folder)
--------------------------------------------------
  __init__.py   <- YOU ARE HERE — public API / entry point
  server.py     <- HTTP router + blocking server loop
  http.py       <- request parser + response helpers
  upload.py     <- multipart/form-data streaming upload parser
  ui.py         <- HTML/CSS/JS page builder
  fileops.py    <- rename / copy / move / raw-read / save
  wifi.py       <- STA connect + AP mode helpers
  utils.py      <- URL codec, fs helpers, auth, constants
"""

__version__ = '1.0.0'
__author__  = 'Rakib Hasan'
__github__  = 'https://github.com/thezerohz'
__license__ = 'MIT'

# Relative imports — work correctly whether the package lives at the root,
# in /lib/, or in any other sub-directory on the device.
from .wifi   import connect_sta, start_ap
from .server import run
from .utils  import fmt_size, disk_stats, list_dir   # optional helpers


_BANNER = """\
+-------------------------------------------------+
|  WebFileManager  v{version:<28}  |
|  MicroPython Web File Manager                   |
|  by Rakib Hasan  github.com/thezerohz          |
+-------------------------+-----------------------+
|  URL   http://{ip:<32}  |
|  Root  {root:<40}  |
{auth_line}+-------------------------+-----------------------+"""

_AUTH_LINE_FMT = "|  Auth  {:<40}  |\n"
_NO_AUTH_LINE  = _AUTH_LINE_FMT.format("(none — open access)")


def start(
    ssid='',
    password='',
    port=8080,
    root='/',
    http_user='',
    http_pass='',
    timeout=20,
    # Access-Point mode
    ap_mode=False,
    ap_ssid='WebFM',
    ap_pass='micropython',
):
    """
    Start the WebFileManager HTTP server.  Blocks forever.

    Parameters
    ----------
    ssid       : WiFi SSID to join (STA mode)
    password   : WiFi password     (STA mode)
    port       : HTTP port  (default 8080)
    root       : filesystem root exposed to the browser  (default '/')
    http_user  : Basic-auth username  (empty = no auth required)
    http_pass  : Basic-auth password
    timeout    : WiFi connect timeout in seconds  (default 20)
    ap_mode    : if True, create an Access Point instead of joining a network
    ap_ssid    : AP network name  (default 'WebFM')
    ap_pass    : AP password  (empty string = open / no password)

    Examples
    --------
    # Join your home WiFi:
    import WebFileManager
    WebFileManager.start(ssid="MyWifi", password="secret")

    # Standalone hotspot (no router needed):
    WebFileManager.start(ap_mode=True, ap_ssid="ESP32Files", ap_pass="12345678")

    # Password-protected, custom port, expose only /sd:
    WebFileManager.start(
        ssid="MyWifi", password="secret",
        port=80, root="/sd",
        http_user="admin", http_pass="admin",
    )
    """
    if ap_mode:
        ip = start_ap(ap_ssid, ap_pass)
    else:
        if not ssid:
            raise ValueError('ssid is required when ap_mode=False')
        ip = connect_sta(ssid, password, timeout)

    addr      = '{}:{}'.format(ip, port)
    auth_line = (_AUTH_LINE_FMT.format('{}:*****'.format(http_user))
                 if http_user else _NO_AUTH_LINE)

    print(_BANNER.format(
        version   = __version__,
        ip        = addr,
        root      = root,
        auth_line = auth_line,
    ))

    run(ip, port, root, http_user, http_pass)
