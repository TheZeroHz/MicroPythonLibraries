"""
http.py — low-level HTTP request parsing and response helpers
WebFileManager by Rakib Hasan (@thezerohz) — https://github.com/thezerohz
"""


# ─── request parser ────────────────────────────────────────────────────────────

def recv_request(conn):
    """
    Read HTTP request line + headers from conn.
    Returns (method, path, qs, headers, leftover_body_bytes).
    """
    raw = b''
    while b'\r\n\r\n' not in raw:
        chunk = conn.recv(256)
        if not chunk:
            break
        raw += chunk
        if len(raw) > 8192:
            break

    sep = raw.find(b'\r\n\r\n')
    leftover = raw[sep + 4:] if sep != -1 else b''
    header_section = (raw[:sep] if sep != -1 else raw).decode('utf-8', 'ignore')

    lines = header_section.split('\r\n')
    if not lines:
        return None, None, '', {}, b''

    req_parts = lines[0].split(' ')
    if len(req_parts) < 2:
        return None, None, '', {}, b''

    method    = req_parts[0]
    full_path = req_parts[1]

    if '?' in full_path:
        path, qs = full_path.split('?', 1)
    else:
        path, qs = full_path, ''

    headers = {}
    for line in lines[1:]:
        if ':' in line:
            k, v = line.split(':', 1)
            headers[k.strip()] = v.strip()

    return method, path, qs, headers, leftover


# ─── response helpers ──────────────────────────────────────────────────────────

def send_redirect(conn, location):
    loc = location.encode()
    conn.sendall(
        b'HTTP/1.1 302 Found\r\nLocation: ' + loc +
        b'\r\nContent-Length: 0\r\nConnection: close\r\n\r\n'
    )


def send_html(conn, html, status=200):
    body = html.encode('utf-8')
    status_line = 'HTTP/1.1 {} OK\r\n'.format(status).encode()
    conn.sendall(
        status_line +
        b'Content-Type: text/html; charset=utf-8\r\n' +
        b'Content-Length: ' + str(len(body)).encode() + b'\r\n' +
        b'Connection: close\r\n\r\n' + body
    )


def send_json(conn, data, status=200):
    import json as _json
    body = _json.dumps(data).encode('utf-8')
    status_line = 'HTTP/1.1 {} OK\r\n'.format(status).encode()
    conn.sendall(
        status_line +
        b'Content-Type: application/json\r\n' +
        b'Content-Length: ' + str(len(body)).encode() + b'\r\n' +
        b'Connection: close\r\n\r\n' + body
    )


def send_file(conn, filepath, stat_size_fn):
    """Stream a file to the client in 1 kB chunks."""
    try:
        size = stat_size_fn(filepath)
        name = filepath.split('/')[-1]
        conn.sendall(
            b'HTTP/1.1 200 OK\r\n'
            b'Content-Type: application/octet-stream\r\n'
            b'Content-Disposition: attachment; filename="' + name.encode() + b'"\r\n'
            b'Content-Length: ' + str(size).encode() + b'\r\n'
            b'Connection: close\r\n\r\n'
        )
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(1024)
                if not chunk:
                    break
                conn.sendall(chunk)
    except OSError as e:
        send_html(conn, '<h1>Error: {}</h1>'.format(e), 500)


def send_404(conn):
    send_html(conn, '<h1>404 Not Found</h1>', 404)


def send_400(conn, msg='Bad Request'):
    send_html(conn, '<h1>400 {}</h1>'.format(msg), 400)


def send_auth_required(conn):
    body = b'<h1>401 Unauthorized</h1>'
    conn.sendall(
        b'HTTP/1.1 401 Unauthorized\r\n'
        b'WWW-Authenticate: Basic realm="FileManager"\r\n'
        b'Content-Type: text/html\r\n'
        b'Content-Length: ' + str(len(body)).encode() + b'\r\n'
        b'Connection: close\r\n\r\n' + body
    )


def recv_exactly(conn, n, chunk_size=4096):
    """Read exactly n bytes, return bytes object."""
    data = b''
    while len(data) < n:
        chunk = conn.recv(min(chunk_size, n - len(data)))
        if not chunk:
            break
        data += chunk
    return data
