"""
rtttl
~~~~~
RTTTL (Ring Tone Text Transfer Language) library for MicroPython.
Tested on Raspberry Pi Pico W.

Typical usage
-------------
Blocking (simplest)::

    from rtttl import PlayRtttl
    from rtttl.melodies import RTTTL_MELODIES

    player = PlayRtttl(pin=8)
    player.play_blocking(RTTTL_MELODIES[21])  # Nokia tune

Non-blocking (use in a main loop)::

    player = PlayRtttl(pin=8)
    player.start(RTTTL_MELODIES[0])

    while True:
        player.update()
        # … other work here …

Module layout
-------------
rtttl/
  __init__.py   ← public re-exports (this file)
  constants.py  ← note table, style constants, defaults
  notes.py      ← frequency calculation, style-char conversion
  parser.py     ← RTTTL header + note-token parser
  player.py     ← PlayRtttl (PWM driver, state machine)
  melodies.py   ← built-in RTTTL strings
"""

from .constants import (
    STYLE_CONTINUOUS,
    STYLE_NATURAL,
    STYLE_STACCATO,
    STYLE_4,
    STYLE_8,
    STYLE_DEFAULT,
    DEFAULT_DURATION,
    DEFAULT_OCTAVE,
    DEFAULT_BPM,
)
from .notes import get_frequency, style_char_to_divisor
from .parser import parse_header, parse_next_note, SongHeader
from .player import PlayRtttl

__all__ = [
    # Player
    "PlayRtttl",
    # Parser
    "parse_header",
    "parse_next_note",
    "SongHeader",
    # Notes
    "get_frequency",
    "style_char_to_divisor",
    # Constants
    "STYLE_CONTINUOUS",
    "STYLE_NATURAL",
    "STYLE_STACCATO",
    "STYLE_4",
    "STYLE_8",
    "STYLE_DEFAULT",
    "DEFAULT_DURATION",
    "DEFAULT_OCTAVE",
    "DEFAULT_BPM",
]
