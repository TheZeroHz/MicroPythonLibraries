"""
rtttl/player.py
~~~~~~~~~~~~~~~
Non-blocking and blocking RTTTL player for MicroPython (Raspberry Pi Pico W).

Usage example::

    from rtttl.player import PlayRtttl
    from rtttl.melodies import RTTTL_MELODIES

    player = PlayRtttl(pin=8)
    player.start(RTTTL_MELODIES[0])   # non-blocking

    while player.update():             # call from your main loop
        pass
"""

import time
import random as _random

from machine import PWM, Pin

from .constants import STYLE_DEFAULT
from .notes import get_frequency
from .parser import parse_header, parse_next_note


class PlayRtttl:
    """RTTTL player for MicroPython.

    Args:
        pin:           GPIO pin number connected to the buzzer/speaker.
        style_divisor: Default playback style.  Override per-song via the
                       RTTTL ``s=`` parameter.  Common values:

                       * ``STYLE_NATURAL`` (16)   – slight gap between notes (default)
                       * ``STYLE_STACCATO`` (2)   – short notes with long gaps
                       * ``STYLE_CONTINUOUS`` (0) – notes run end-to-end
    """

    def __init__(self, pin: int, style_divisor: int = STYLE_DEFAULT):
        self._pwm = PWM(Pin(pin))
        self._pwm.freq(1000)       # arbitrary valid starting frequency
        self._pwm.duty_u16(0)      # silent

        self._style_divisor = style_divisor

        # Runtime state
        self._is_running       = False
        self._rtttl            = ""
        self._header           = None
        self._next_idx         = 0
        self._notes_start      = 0
        self._next_action_time = 0
        self._tone_stop_time   = 0
        self._loops_left       = 1
        self._on_complete      = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self, rtttl: str, on_complete=None) -> bool:
        """Begin playback in non-blocking mode.

        Args:
            rtttl:       RTTTL-formatted string.
            on_complete: Optional zero-argument callable invoked when the
                         song (including all loops) finishes.

        Returns:
            ``True`` on success, ``False`` if the header could not be parsed.
        """
        self._header = parse_header(rtttl)
        if self._header.notes_start < 0:
            return False

        # Honour per-song style only if the header specified one explicitly;
        # otherwise fall back to the instance-level default.
        # parse_header already stored the per-song style in _header.style_divisor.
        # We always use _header.style_divisor during playback, so that is fine.

        self._rtttl            = rtttl
        self._notes_start      = self._header.notes_start
        self._next_idx         = self._header.notes_start
        self._loops_left       = max(self._header.number_of_loops, 1)
        self._next_action_time = 0
        self._tone_stop_time   = 0
        self._is_running       = True
        self._on_complete      = on_complete

        self.update()
        return True

    def play_blocking(self, rtttl: str) -> None:
        """Play an RTTTL string synchronously (blocks until finished)."""
        if self.start(rtttl):
            while self.update():
                time.sleep_ms(1)

    def update(self) -> bool:
        """Advance the player state machine.

        Call this repeatedly from your main loop (or tight loop for blocking
        use).

        Returns:
            ``True`` while still playing; ``False`` when finished.
        """
        if not self._is_running:
            return False

        now = time.ticks_ms()

        # --- silence the buzzer when the tone portion is over ---
        if self._tone_stop_time and time.ticks_diff(now, self._tone_stop_time) >= 0:
            self._pwm.duty_u16(0)
            self._tone_stop_time = 0

        # --- not yet time for the next note ---
        if time.ticks_diff(now, self._next_action_time) < 0:
            return True

        # --- end of notes string ---
        if self._next_idx >= len(self._rtttl):
            if self._loops_left > 1:
                self._loops_left -= 1
                self._next_idx = self._notes_start
                return self.update()
            self._finish()
            return False

        # --- parse and play next note ---
        note_index, octave, duration_ms, self._next_idx = parse_next_note(
            self._rtttl, self._next_idx, self._header
        )

        style = self._header.style_divisor if self._header.style_divisor != STYLE_DEFAULT \
                else self._style_divisor

        if note_index <= 11:          # pitched note
            freq = get_frequency(note_index, octave)
            if style != 0:
                tone_ms = duration_ms - ((duration_ms + (style // 2)) // style)
            else:
                tone_ms = duration_ms
            self._pwm.freq(freq)
            self._pwm.duty_u16(32768)  # 50 % duty cycle → square wave
            self._tone_stop_time = now + tone_ms
        else:                         # rest / pause
            self._pwm.duty_u16(0)
            self._tone_stop_time = 0

        self._next_action_time = now + duration_ms
        return True

    def stop(self) -> None:
        """Immediately stop playback and silence the buzzer."""
        self._pwm.duty_u16(0)
        self._tone_stop_time = 0
        self._is_running = False

    def is_playing(self) -> bool:
        """Return ``True`` if playback is in progress."""
        return self._is_running

    # ------------------------------------------------------------------
    # Configuration helpers
    # ------------------------------------------------------------------

    def set_style(self, style_divisor: int) -> None:
        """Change the default playback style at runtime."""
        self._style_divisor = style_divisor

    def set_loops(self, n: int) -> None:
        """Set loop count for the *next* call to :meth:`start` (0 = forever)."""
        # Note: number_of_loops is stored per-song in the SongHeader after
        # parsing; this is a convenience override before calling start().
        self._loops_left = n if n > 0 else 0

    # ------------------------------------------------------------------
    # Convenience: random selection
    # ------------------------------------------------------------------

    def play_random(self, songs: list, on_complete=None) -> str | None:
        """Start a random song from *songs* (non-blocking).

        Returns:
            The selected RTTTL string, or ``None`` if *songs* is empty.
        """
        if not songs:
            return None
        chosen = songs[_random.randint(0, len(songs) - 1)]
        self.start(chosen, on_complete)
        return chosen

    def play_random_blocking(self, songs: list) -> str | None:
        """Play a random song from *songs* (blocking).

        Returns:
            The selected RTTTL string, or ``None`` if *songs* is empty.
        """
        if not songs:
            return None
        chosen = songs[_random.randint(0, len(songs) - 1)]
        self.play_blocking(chosen)
        return chosen

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _finish(self) -> None:
        self.stop()
        if self._on_complete is not None:
            self._on_complete()
