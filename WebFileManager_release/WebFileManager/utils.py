"""
utils.py — shared helpers for WebFileManager
WebFileManager by Rakib Hasan (@thezerohz) — https://github.com/thezerohz
"""

import os
import gc
import binascii


# ─── URL encoding / decoding ──────────────────────────────────────────────────

def unquote(s):
    """Minimal URL-decode (handles %XX and '+')."""
    res = []
    i = 0
    while i < len(s):
        if s[i] == '+':
            res.append(' ')
            i += 1
        elif s[i] == '%' and i + 2 < len(s):
            try:
                res.append(chr(int(s[i+1:i+3], 16)))
                i += 3
            except ValueError:
                res.append(s[i])
                i += 1
        else:
            res.append(s[i])
            i += 1
    return ''.join(res)


def quote(s):
    """Minimal URL-encode for paths (keeps '/' safe)."""
    safe = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~/'
    out = []
    for c in s:
        if c in safe:
            out.append(c)
        else:
            out.append('%{:02X}'.format(ord(c)))
    return ''.join(out)


def parse_qs(qs):
    """Parse a query string into a dict."""
    params = {}
    if not qs:
        return params
    for pair in qs.split('&'):
        if '=' in pair:
            k, v = pair.split('=', 1)
            params[unquote(k)] = unquote(v)
    return params


# ─── filesystem helpers ────────────────────────────────────────────────────────

def stat_size(path):
    try:
        return os.stat(path)[6]
    except OSError:
        return 0


def is_dir(path):
    try:
        return (os.stat(path)[0] & 0x4000) != 0
    except OSError:
        return False


def join_path(a, b):
    if a.endswith('/'):
        return a + b
    return a + '/' + b


def list_dir(root, path):
    """Return list of (name, size, is_dir) for path, dirs first."""
    full = join_path(root.rstrip('/'), path.lstrip('/')) if path != '/' else root
    entries = []
    try:
        for name in os.listdir(full):
            fpath = join_path(full, name)
            d = is_dir(fpath)
            sz = 0 if d else stat_size(fpath)
            entries.append((name, sz, d))
    except OSError:
        pass
    entries.sort(key=lambda e: (not e[2], e[0].lower()))
    return entries


def fmt_size(n):
    for unit in ('B', 'kB', 'MB', 'GB'):
        if n < 1024:
            return '{} {}'.format(n, unit)
        n //= 1024
    return '{} TB'.format(n)


def disk_stats(root):
    try:
        st = os.statvfs(root)
        total = st[0] * st[2]
        free  = st[0] * st[3]
        used  = total - free
        return fmt_size(free), fmt_size(used), fmt_size(total)
    except OSError:
        return '?', '?', '?'


def sanitise_name(name):
    """Remove path-traversal chars; return safe filename."""
    return name.replace('..', '').replace('\\', '').replace('/', '').strip()


def resolve(root, vpath):
    """Turn a virtual path (from URL) into an absolute filesystem path."""
    vpath = vpath.lstrip('/')
    if not vpath:
        return root.rstrip('/')
    return join_path(root.rstrip('/'), vpath)


# ─── authentication ───────────────────────────────────────────────────────────

def b64encode(s):
    return binascii.b2a_base64(s.encode()).decode().strip()


def check_auth(headers, user, pwd):
    if not user:
        return True
    expected = 'Basic ' + b64encode('{}:{}'.format(user, pwd))
    return headers.get('Authorization', '') == expected


# ─── PSRAM / heap allocation helper ──────────────────────────────────────────

def has_psram():
    """Best-effort check: ESP32 with PSRAM has large free heap."""
    try:
        gc.collect()
        return gc.mem_free() > 1_000_000
    except Exception:
        return False


CHUNK_SIZE = 4096   # bytes per read chunk during upload streaming
