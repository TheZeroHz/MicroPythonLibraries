"""
rtttl/notes.py
~~~~~~~~~~~~~~
Note-index ↔ frequency helpers and style-char conversion.
"""

from .constants import NOTES, NOTES_OCTAVE, STYLE_DEFAULT


def get_frequency(note_index: int, octave: int) -> int:
    """
    Return the frequency (Hz) for a chromatic note index and octave.

    Args:
        note_index: 0–11  (C=0, C#=1, … B=11); any other value means pause.
        octave:     3–7

    Returns:
        Frequency in Hz, or 0 for a pause.
    """
    if note_index >= len(NOTES):
        return 0  # pause

    freq = NOTES[note_index]
    if octave <= NOTES_OCTAVE:
        freq >>= (NOTES_OCTAVE - octave)
    else:
        freq <<= (octave - NOTES_OCTAVE)
    return freq


def style_char_to_divisor(char: str) -> int:
    """
    Convert an RTTTL style character to a divisor value.

    Args:
        char: 'S' (staccato), 'N' (natural), 'C' (continuous), or '1'–'9'.

    Returns:
        Integer divisor.
    """
    if char == 'S':
        return 2
    if char == 'N':
        return 16
    if char == 'C':
        return 0
    if '1' <= char <= '9':
        return int(char)
    return STYLE_DEFAULT
