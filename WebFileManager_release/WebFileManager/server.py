"""
server.py — HTTP server and request router for WebFileManager
WebFileManager by Rakib Hasan (@thezerohz) — https://github.com/thezerohz

Route table
-----------
GET  /                  → directory listing
POST /                  → upload files (multipart/form-data)
GET  /download          → stream a file to client
GET  /delete            → delete file or empty dir
GET  /mkdir             → create directory
GET  /rename            → rename file/dir  (JSON response)
GET  /fileop            → copy or move     (JSON response)
GET  /raw               → fetch raw file text (for editor)
POST /save              → save text file (from editor)
"""

import socket
import gc
from .utils import resolve, is_dir, quote, parse_qs, check_auth
from .http import (
    recv_request, send_redirect, send_html, send_file,
    send_404, send_auth_required, stat_size as _stat_noop
)
from .ui import build_page
from .upload import parse_multipart_upload
from .fileops import handle_rename, handle_fileop, handle_raw, handle_save


# ─── request dispatcher ───────────────────────────────────────────────────────

def _handle(conn, addr, root, http_user, http_pass):
    try:
        method, path, qs, headers, leftover = recv_request(conn)
        if method is None:
            return

        if not check_auth(headers, http_user, http_pass):
            send_auth_required(conn)
            return

        params = parse_qs(qs)

        # ── GET / : directory listing ─────────────────────────────────────────
        if method == 'GET' and path == '/':
            current = params.get('path', '/')
            if not current.startswith('/'):
                current = '/' + current
            html = build_page(root, current)
            send_html(conn, html)

        # ── POST / : file upload ──────────────────────────────────────────────
        elif method == 'POST' and path == '/':
            current = params.get('path', '/')
            dest    = resolve(root, current)
            ct      = headers.get('Content-Type', '')
            cl      = int(headers.get('Content-Length', 0))
            parse_multipart_upload(conn, ct, cl, dest, leftover=leftover)
            # Return 200 so XHR upload-progress handler can detect success
            send_html(conn, '<ok>', 200)

        # ── GET /download : send file ─────────────────────────────────────────
        elif method == 'GET' and path == '/download':
            fpath = params.get('path', '')
            if not fpath:
                send_404(conn)
                return
            abs_path = resolve(root, fpath)
            if is_dir(abs_path):
                send_404(conn)
            else:
                from .utils import stat_size
                send_file(conn, abs_path, stat_size)

        # ── GET /delete : remove file or empty dir ────────────────────────────
        elif method == 'GET' and path == '/delete':
            import os
            fpath = params.get('path', '')
            back  = params.get('back', '/')
            if fpath:
                abs_path = resolve(root, fpath)
                try:
                    if is_dir(abs_path):
                        os.rmdir(abs_path)
                    else:
                        os.remove(abs_path)
                except OSError:
                    pass
            send_redirect(conn, '/?path=' + quote(back))

        # ── GET /mkdir : create directory ─────────────────────────────────────
        elif method == 'GET' and path == '/mkdir':
            import os
            from utils import sanitise_name, join_path
            current = params.get('path', '/')
            name    = sanitise_name(params.get('name', ''))
            if name:
                abs_dir = resolve(root, current)
                new_dir = join_path(abs_dir, name)
                try:
                    os.mkdir(new_dir)
                except OSError:
                    pass
            send_redirect(conn, '/?path=' + quote(current))

        # ── GET /rename : rename file/dir (JSON) ──────────────────────────────
        elif method == 'GET' and path == '/rename':
            handle_rename(conn, params, root)

        # ── GET /fileop : copy or move (JSON) ─────────────────────────────────
        elif method == 'GET' and path == '/fileop':
            handle_fileop(conn, params, root)

        # ── GET /raw : raw file content for editor ────────────────────────────
        elif method == 'GET' and path == '/raw':
            handle_raw(conn, params, root)

        # ── POST /save : save editor content ─────────────────────────────────
        elif method == 'POST' and path == '/save':
            handle_save(conn, params, headers, root, leftover=leftover)

        else:
            send_404(conn)

    except OSError:
        pass
    finally:
        conn.close()
        gc.collect()


# ─── server loop ──────────────────────────────────────────────────────────────

def run(ip, port, root, http_user, http_pass):
    """Blocking server loop. Call after WiFi is up."""
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('', port))
    srv.listen(3)

    print('[WebFM] Listening on http://{}:{}/'.format(ip, port))

    while True:
        try:
            conn, addr = srv.accept()
            conn.settimeout(15)
            _handle(conn, addr, root, http_user, http_pass)
        except OSError:
            pass
        gc.collect()
