# WebFileManager

> A modular, browser-based file manager for MicroPython devices.  
> **by [Rakib Hasan (@thezerohz)](https://github.com/thezerohz)**  
> Import it like a proper Python package — `import WebFileManager`

---

## Features

| Feature | Details |
|---|---|
| **Browse** | Directory tree, breadcrumb navigation, file/folder icons, disk usage bar |
| **Upload** | Multi-file, drag-and-drop, live progress bar with speed indicator |
| **Download** | Single-file streamed download |
| **Delete** | Files and empty directories with confirm dialog |
| **Rename** | Inline modal rename for files and folders |
| **Copy / Move** | Modal with destination path field, recursive directory support |
| **Text editor** | Inline editor for `.py`, `.json`, `.html`, `.txt`, `.yaml`, etc. |
| **Create folder** | Toolbar input |
| **Auth** | Optional HTTP Basic Auth |
| **AP mode** | Start as Access Point — no router needed |

---

## Installation

Copy the `WebFileManager/` **folder** to your device.  
It can live right next to `main.py` **or** inside `/lib/` — both work.

```
/                          <- device root  (or /lib/)
├── main.py
└── WebFileManager/        <- the whole folder goes here
    ├── __init__.py
    ├── server.py
    ├── http.py
    ├── upload.py
    ├── ui.py
    ├── fileops.py
    ├── wifi.py
    └── utils.py
```

**Using mpremote (recommended):**
```bash
mpremote connect PORT cp -r WebFileManager/ :
```

**Using rshell:**
```bash
rshell -p /dev/ttyUSB0 cp -r WebFileManager /pyboard/
```

**Using Thonny:** drag the folder onto your device in the Files panel.

---

## Quick start

```python
# main.py — join your WiFi network
import WebFileManager

WebFileManager.start(ssid="MyWifi", password="secret")
# Open browser → http://<device-ip>:8080/
```

```python
# main.py — standalone Access Point (no router needed)
import WebFileManager

WebFileManager.start(ap_mode=True, ap_ssid="PicoFiles", ap_pass="micropython")
# Connect phone/laptop to "PicoFiles" WiFi, then → http://192.168.4.1/
```

---

## All options

```python
WebFileManager.start(
    # STA (client) mode — join existing WiFi
    ssid       = "MyWifi",
    password   = "secret",
    timeout    = 20,          # WiFi connect timeout in seconds

    # AP mode — create a hotspot (overrides STA when ap_mode=True)
    ap_mode    = False,
    ap_ssid    = "WebFM",
    ap_pass    = "micropython",  # set '' for an open/passwordless AP

    # Server settings
    port       = 8080,        # HTTP port
    root       = "/",         # filesystem root to expose in browser

    # Optional HTTP Basic Auth (leave blank to disable)
    http_user  = "admin",
    http_pass  = "admin",
)
```

---

## Importing sub-modules directly

The package exposes a few helpers you can import without starting the server:

```python
from WebFileManager import fmt_size, disk_stats, list_dir

free, used, total = disk_stats('/')
print("Free:", free, "/ Total:", total)

for name, size, is_dir in list_dir('/', '/'):
    print(name, "" if is_dir else fmt_size(size))
```

You can also reach into sub-modules:

```python
from WebFileManager.utils import join_path, resolve, sanitise_name, quote, unquote
from WebFileManager.wifi  import connect_sta, start_ap
from WebFileManager.http  import recv_request, send_html, send_json, send_file
```

---

## HTTP API reference

| Method | Path | Description | Response |
|---|---|---|---|
| `GET` | `/?path=/dir` | Directory listing | HTML page |
| `POST` | `/?path=/dir` | Upload files (multipart/form-data) | `200 <ok>` |
| `GET` | `/download?path=/file.txt` | Download a file | Binary stream |
| `GET` | `/delete?path=/file.txt&back=/` | Delete file or empty dir | 302 redirect |
| `GET` | `/mkdir?path=/dir&name=newfolder` | Create a directory | 302 redirect |
| `GET` | `/rename?src=/old.txt&name=new.txt` | Rename file/dir | `{"ok": true}` |
| `GET` | `/fileop?op=copy&src=/a.txt&dest=/b.txt` | Copy file/dir | `{"ok": true}` |
| `GET` | `/fileop?op=move&src=/a.txt&dest=/b/` | Move file/dir | `{"ok": true}` |
| `GET` | `/raw?path=/file.txt` | Get raw file content | Plain text |
| `POST` | `/save?path=/file.txt` | Overwrite file (body = new content) | `200 OK` |

---

## Module layout

| File | Responsibility |
|---|---|
| `__init__.py` | Public API — `start()` entry point, boot banner |
| `server.py` | HTTP request router + blocking server loop |
| `http.py` | Request parser, all response helpers |
| `upload.py` | Multipart streaming upload parser |
| `ui.py` | Full HTML/CSS/JS page builder (inlined, no external deps) |
| `fileops.py` | Rename, copy, move, raw file read, save |
| `wifi.py` | STA connect + AP mode helpers |
| `utils.py` | URL codec, filesystem helpers, auth, constants |

---

## Supported devices

- MicroPython v1.23+
- ESP32-WROOM, ESP32-S3 (with or without PSRAM)
- RP2040-W (Raspberry Pi Pico W)
- Any MicroPython board with WiFi and the `network` module

---

## Credits

**WebFileManager** is written and maintained by  
**Rakib Hasan** · [@thezerohz](https://github.com/thezerohz) · [github.com/thezerohz](https://github.com/thezerohz)

---

## License

MIT — free to use, modify, and distribute with attribution.
