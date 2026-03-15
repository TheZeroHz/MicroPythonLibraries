"""
rtttl/constants.py
~~~~~~~~~~~~~~~~~~
Shared constants for the RTTTL library.
"""

# Note frequencies for octave 7 (all other octaves derived by bit-shifting)
NOTES_OCTAVE = 7
NOTES = [
    2093,  # C7
    2217,  # C#7
    2349,  # D7
    2489,  # D#7
    2637,  # E7
    2794,  # F7
    2960,  # F#7
    3136,  # G7
    3322,  # G#7
    3520,  # A7
    3729,  # A#7
    3951,  # B7
]

# Song-header defaults
DEFAULT_DURATION = 4
DEFAULT_OCTAVE   = 6
DEFAULT_BPM      = 63

# Playback style divisors
STYLE_CONTINUOUS = 0   # tone length == note length
STYLE_NATURAL    = 16  # tone length = note length - 1/16
STYLE_STACCATO   = 2   # tone length = note length - 1/2
STYLE_4          = 4   # tone length = note length - 1/4
STYLE_8          = 8   # tone length = note length - 1/8
STYLE_DEFAULT    = STYLE_NATURAL
