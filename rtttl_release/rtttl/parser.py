"""
rtttl/parser.py
~~~~~~~~~~~~~~~
Parse RTTTL strings into song parameters and individual notes.

RTTTL format:
    Name:d=<duration>,o=<octave>,b=<bpm>[,l=<loops>][,s=<style>]:<note>,<note>,...
"""

from .constants import DEFAULT_DURATION, DEFAULT_OCTAVE, DEFAULT_BPM, STYLE_DEFAULT
from .notes import style_char_to_divisor


class SongHeader:
    """Holds parsed header parameters for one RTTTL string."""

    def __init__(self):
        self.name             = ""
        self.default_duration = DEFAULT_DURATION
        self.default_octave   = DEFAULT_OCTAVE
        self.bpm              = DEFAULT_BPM
        self.time_for_whole_note_ms = (60_000 // DEFAULT_BPM) * 4
        self.number_of_loops  = 1
        self.style_divisor    = STYLE_DEFAULT
        self.notes_start      = -1   # index into the original string where notes begin


def parse_header(rtttl: str) -> SongHeader:
    """
    Parse the name/parameter section of an RTTTL string.

    Args:
        rtttl: Full RTTTL string.

    Returns:
        Populated SongHeader.  header.notes_start == -1 on parse failure.
    """
    h = SongHeader()
    idx = 0

    # --- name ---
    while idx < len(rtttl) and rtttl[idx] != ':':
        idx += 1
    h.name = rtttl[:idx]

    if idx >= len(rtttl):
        return h  # notes_start stays -1

    idx += 1  # skip first ':'

    # --- parameters ---
    while idx < len(rtttl) and rtttl[idx] != ':':
        ch = rtttl[idx]

        if ch == 'd':               # default duration
            idx += 2
            num, idx = _read_int(rtttl, idx)
            if num > 0:
                h.default_duration = num

        elif ch == 'o':             # default octave
            idx += 2
            if idx < len(rtttl) and rtttl[idx].isdigit():
                num = int(rtttl[idx])
                idx += 1
                if 3 <= num <= 7:
                    h.default_octave = num

        elif ch == 'b':             # BPM
            idx += 2
            bpm, idx = _read_int(rtttl, idx)
            if bpm > 0:
                h.bpm = bpm
                h.time_for_whole_note_ms = (60_000 // bpm) * 4

        elif ch == 'l':             # loop count
            idx += 2
            num, idx = _read_int(rtttl, idx)
            if num == 15:
                num = 0             # 15 → loop forever
            h.number_of_loops = num

        elif ch == 's':             # style
            idx += 2
            if idx < len(rtttl):
                h.style_divisor = style_char_to_divisor(rtttl[idx])
                idx += 1
        else:
            idx += 1

    if idx >= len(rtttl):
        return h  # notes_start stays -1

    idx += 1  # skip second ':'
    h.notes_start = idx
    return h


def parse_next_note(rtttl: str, idx: int, header: SongHeader):
    """
    Parse one note token starting at *idx* in *rtttl*.

    Args:
        rtttl:  Full RTTTL string.
        idx:    Current parse position (points to first char of the token).
        header: SongHeader with default_duration, default_octave,
                time_for_whole_note_ms.

    Returns:
        Tuple ``(note_index, octave, duration_ms, next_idx)`` where:
            note_index  – 0–11 for a pitched note; 42 for a rest/pause
            octave      – octave number (3–7)
            duration_ms – note duration in milliseconds
            next_idx    – index to pass on the next call (past trailing comma)
    """
    # --- duration digits ---
    duration_num, idx = _read_int(rtttl, idx)
    if duration_num == 0:
        duration_num = header.default_duration
    duration_ms = header.time_for_whole_note_ms // duration_num

    if idx >= len(rtttl):
        return 42, header.default_octave, duration_ms, idx

    # --- note letter ---
    note_char = rtttl[idx].lower()
    note_index = 42  # default = pause

    _NOTE_MAP = {
        'c': 0, 'd': 2, 'e': 4, 'f': 5,
        'g': 7, 'a': 9, 'b': 11, 'h': 11,
        'p': 42,
    }
    note_index = _NOTE_MAP.get(note_char, 42)
    idx += 1

    # --- sharp / flat ---
    if idx < len(rtttl) and rtttl[idx] in ('#', '_'):
        if note_index <= 11:
            note_index += 1
        idx += 1

    # --- first dot ---
    if idx < len(rtttl) and rtttl[idx] == '.':
        duration_ms += duration_ms // 2
        idx += 1

    # --- octave digit ---
    if idx < len(rtttl) and rtttl[idx].isdigit():
        octave = int(rtttl[idx])
        idx += 1
    else:
        octave = header.default_octave

    # --- second dot (rare) ---
    if idx < len(rtttl) and rtttl[idx] == '.':
        duration_ms += duration_ms // 2
        idx += 1

    # --- skip comma separator ---
    if idx < len(rtttl) and rtttl[idx] == ',':
        idx += 1

    return note_index, octave, duration_ms, idx


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _read_int(s: str, idx: int):
    """Read consecutive digit characters starting at idx.  Returns (value, new_idx)."""
    num = 0
    while idx < len(s) and s[idx].isdigit():
        num = num * 10 + int(s[idx])
        idx += 1
    return num, idx
