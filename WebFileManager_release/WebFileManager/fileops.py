"""
fileops.py — file operation handlers: rename, copy, move, save (text edit)
WebFileManager by Rakib Hasan (@thezerohz) — https://github.com/thezerohz

All functions accept (conn, params, root) and send a response directly.
"""

import os
import gc
from .utils import resolve, join_path, sanitise_name, is_dir, quote, CHUNK_SIZE
from .http import send_json, send_redirect, send_html, recv_exactly, send_400


# ─── rename ──────────────────────────────────────────────────────────────────

def handle_rename(conn, params, root):
    """
    GET /rename?src=<vpath>&name=<new_name>
    Renames (moves) a file or dir within the same parent folder.
    """
    src_vpath = params.get('src', '')
    new_name  = sanitise_name(params.get('name', ''))

    if not src_vpath or not new_name:
        send_json(conn, {'ok': False, 'error': 'missing params'}, 400)
        return

    abs_src = resolve(root, src_vpath)
    parent  = '/'.join(abs_src.rstrip('/').split('/')[:-1]) or root
    abs_dst = join_path(parent, new_name)

    try:
        os.rename(abs_src, abs_dst)
        send_json(conn, {'ok': True})
    except OSError as e:
        send_json(conn, {'ok': False, 'error': str(e)}, 500)


# ─── copy ─────────────────────────────────────────────────────────────────────

def _copy_file(src, dst):
    """Copy a single file chunk by chunk."""
    with open(src, 'rb') as fin, open(dst, 'wb') as fout:
        while True:
            chunk = fin.read(CHUNK_SIZE)
            if not chunk:
                break
            fout.write(chunk)
    gc.collect()


def _copy_tree(src, dst):
    """Recursively copy a directory tree."""
    try:
        os.mkdir(dst)
    except OSError:
        pass
    for entry in os.listdir(src):
        s = join_path(src, entry)
        d = join_path(dst, entry)
        if is_dir(s):
            _copy_tree(s, d)
        else:
            _copy_file(s, d)


def handle_fileop(conn, params, root):
    """
    GET /fileop?op=copy|move&src=<vpath>&dest=<vpath>
    dest is an absolute virtual path (e.g. /subdir/newname.txt).
    If dest ends with '/' or is an existing dir, filename is preserved.
    """
    op        = params.get('op', '')
    src_vpath = params.get('src', '')
    dst_vpath = params.get('dest', '')

    if op not in ('copy', 'move') or not src_vpath or not dst_vpath:
        send_json(conn, {'ok': False, 'error': 'bad params'}, 400)
        return

    abs_src = resolve(root, src_vpath)
    abs_dst = resolve(root, dst_vpath)

    # if dest is/will be a directory, append source filename
    if is_dir(abs_dst) or dst_vpath.endswith('/'):
        fname   = abs_src.rstrip('/').split('/')[-1]
        abs_dst = join_path(abs_dst, fname)

    try:
        if op == 'copy':
            if is_dir(abs_src):
                _copy_tree(abs_src, abs_dst)
            else:
                _copy_file(abs_src, abs_dst)
        else:  # move
            os.rename(abs_src, abs_dst)
        send_json(conn, {'ok': True})
    except OSError as e:
        send_json(conn, {'ok': False, 'error': str(e)}, 500)


# ─── raw file read (for editor) ───────────────────────────────────────────────

def handle_raw(conn, params, root):
    """
    GET /raw?path=<vpath>
    Returns raw text content of a file (for the inline editor).
    """
    vpath = params.get('path', '')
    if not vpath:
        send_html(conn, '', 400)
        return

    abs_path = resolve(root, vpath)
    if is_dir(abs_path):
        send_html(conn, 'Is a directory', 400)
        return

    try:
        size = 0
        try:
            import os as _os
            size = _os.stat(abs_path)[6]
        except OSError:
            pass

        conn.sendall(
            b'HTTP/1.1 200 OK\r\n'
            b'Content-Type: text/plain; charset=utf-8\r\n'
            b'Content-Length: ' + str(size).encode() + b'\r\n'
            b'Connection: close\r\n\r\n'
        )
        with open(abs_path, 'rb') as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                conn.sendall(chunk)
    except OSError as e:
        conn.sendall(b'HTTP/1.1 500 Error\r\nContent-Length: 0\r\nConnection: close\r\n\r\n')


# ─── save file (from editor) ──────────────────────────────────────────────────

def handle_save(conn, params, headers, root, leftover=b''):
    """
    POST /save?path=<vpath>
    Body: raw text (Content-Type: text/plain).
    Overwrites the file at vpath with the posted body.
    """
    vpath = params.get('path', '')
    if not vpath:
        send_html(conn, 'Missing path', 400)
        return

    abs_path = resolve(root, vpath)
    cl = int(headers.get('Content-Length', 0))
    if cl <= 0:
        send_html(conn, 'Empty body', 400)
        return

    # read remaining body
    remaining = cl - len(leftover)
    body = leftover + (recv_exactly(conn, remaining) if remaining > 0 else b'')

    try:
        with open(abs_path, 'wb') as f:
            f.write(body)
        conn.sendall(
            b'HTTP/1.1 200 OK\r\nContent-Length: 2\r\n'
            b'Connection: close\r\n\r\nOK'
        )
    except OSError as e:
        send_html(conn, 'Save error: {}'.format(e), 500)
    finally:
        gc.collect()
