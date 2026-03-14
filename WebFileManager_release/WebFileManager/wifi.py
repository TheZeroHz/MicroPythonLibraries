"""
wifi.py — WiFi connection helper for WebFileManager
WebFileManager by Rakib Hasan (@thezerohz) — https://github.com/thezerohz
Supports STA (station/client) mode and AP (access point) mode.
"""

import network
import time


def connect_sta(ssid, password, timeout=20):
    """
    Connect to an existing WiFi network.
    Returns the assigned IP address string.
    Raises OSError on timeout.
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        print('[WebFM] Already connected. IP:', wlan.ifconfig()[0])
        return wlan.ifconfig()[0]

    print('[WebFM] Connecting to "{}"'.format(ssid), end='')
    wlan.connect(ssid, password)

    t = 0
    while not wlan.isconnected() and t < timeout:
        time.sleep(0.5)
        print('.', end='')
        t += 0.5

    print()
    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print('[WebFM] Connected! IP:', ip)
        return ip
    raise OSError('[WebFM] Connection to "{}" timed out'.format(ssid))


def start_ap(ssid='WebFM', password='micropython', channel=6):
    """
    Start an access-point so devices can connect directly (no router needed).
    Returns the AP IP (usually 192.168.4.1).
    """
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    # authmode 3 = WPA2-PSK; 0 = open
    authmode = 3 if password else 0
    ap.config(essid=ssid, password=password, authmode=authmode, channel=channel)

    t = 0
    while not ap.active() and t < 10:
        time.sleep(0.2)
        t += 0.2

    ip = ap.ifconfig()[0]
    print('[WebFM] AP started. SSID="{}"  IP: {}'.format(ssid, ip))
    return ip
