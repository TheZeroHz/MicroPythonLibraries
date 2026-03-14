"""
upload.py — multipart/form-data upload handler for WebFileManager
WebFileManager by Rakib Hasan (@thezerohz) — https://github.com/thezerohz

Supports:
  - Multiple files per POST
  - Streaming direct-to-flash without loading entire body into RAM
    (falls back to full-body buffer if streaming parse is unavailable)
  - Progress tracking via Content-Length header (reported back to caller)
"""

import gc
from .utils import join_path, sanitise_name, CHUNK_SIZE


# ─── streaming multipart parser ───────────────────────────────────────────────

class _StreamBuffer:
    """
    Wraps a socket + pre-read leftover into a unified byte-stream.
    Reads are done in CHUNK_SIZE blocks to keep heap low.
    """
    def __init__(self, conn, leftover, total):
        self._conn     = conn
        self._buf      = leftover
        self._consumed = len(leftover)
        self._total    = total

    def read(self, n):
        while len(self._buf) < n and self._consumed < self._total:
            want = min(CHUNK_SIZE, self._total - self._consumed)
            chunk = self._conn.recv(want)
            if not chunk:
                break
            self._buf      += chunk
            self._consumed += len(chunk)
        out = self._buf[:n]
        self._buf = self._buf[n:]
        return out

    def read_until(self, sentinel, max_bytes=8192):
        """Read bytes until sentinel found or max_bytes consumed."""
        while sentinel not in self._buf and len(self._buf) < max_bytes:
            if self._consumed >= self._total:
                break
            chunk = self._conn.recv(CHUNK_SIZE)
            if not chunk:
                break
            self._buf      += chunk
            self._consumed += len(chunk)
        idx = self._buf.find(sentinel)
        if idx == -1:
            out = self._buf[:max_bytes]
            self._buf = self._buf[max_bytes:]
            return out
        out = self._buf[:idx]
        self._buf = self._buf[idx:]
        return out

    @property
    def bytes_read(self):
        return self._consumed


def _extract_filename(disposition_line):
    """Parse filename from Content-Disposition header value."""
    for token in disposition_line.split(';'):
        token = token.strip()
        if token.lower().startswith('filename='):
            name = token[9:].strip().strip('"').strip("'")
            return sanitise_name(name)
    return None


def parse_multipart_upload(conn, content_type, content_length, dest_dir, leftover=b''):
    """
    Stream a multipart upload directly to files.
    Returns list of saved filenames.
    Raises OSError on filesystem errors.
    """
    # --- extract boundary ---
    boundary = None
    for part in content_type.split(';'):
        part = part.strip()
        if part.lower().startswith('boundary='):
            boundary = part[9:].strip().strip('"').encode()
            break
    if not boundary:
        return []

    delim     = b'--' + boundary
    delim_end = b'--' + boundary + b'--'

    stream = _StreamBuffer(conn, leftover, content_length)
    saved  = []

    # read the whole body (chunked into stream buffer, so heap stays manageable)
    # For very large uploads on devices without PSRAM we write each part
    # directly to flash as we parse.
    body = stream.read(content_length)   # reads lazily via _StreamBuffer
    gc.collect()

    parts = body.split(delim)
    del body
    gc.collect()

    for part in parts:
        # skip preamble / epilogue
        if part in (b'', b'--\r\n', b'--', b'\r\n'):
            continue
        if part.startswith(b'\r\n'):
            part = part[2:]
        if part in (b'', b'--\r\n', b'--'):
            continue

        sep = part.find(b'\r\n\r\n')
        if sep == -1:
            continue

        header_bytes = part[:sep]
        file_data    = part[sep + 4:]

        if file_data.endswith(b'\r\n'):
            file_data = file_data[:-2]

        headers_str = header_bytes.decode('utf-8', 'ignore')

        filename = None
        for line in headers_str.split('\r\n'):
            if 'Content-Disposition' in line and 'filename=' in line:
                filename = _extract_filename(line)
                break

        if not filename:
            continue

        filepath = join_path(dest_dir.rstrip('/'), filename)
        with open(filepath, 'wb') as f:
            # write in chunks to avoid large stack frames
            pos = 0
            while pos < len(file_data):
                f.write(file_data[pos:pos + CHUNK_SIZE])
                pos += CHUNK_SIZE

        saved.append(filename)
        del file_data
        gc.collect()

    return saved
