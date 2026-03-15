"""
example_usage.py
~~~~~~~~~~~~~~~~
Quick-start examples for the RTTTL library on a Raspberry Pi Pico W.
"""

# ---------------------------------------------------------------------------
# 1. Blocking playback — simplest approach
# ---------------------------------------------------------------------------
from rtttl import PlayRtttl
from rtttl.melodies import RTTTL_MELODIES, RTTTL_MELODIES_TINY

BUZZER_PIN = 28

player = PlayRtttl(pin=BUZZER_PIN)

# Play the corrected Nokia ringtone (index 21) and wait until done
player.play_blocking(RTTTL_MELODIES[21])


# ---------------------------------------------------------------------------
# 2. Non-blocking playback — interleave with other work
# ---------------------------------------------------------------------------
import time

player.start(RTTTL_MELODIES[0], on_complete=lambda: print("StarWars done!"))

while player.is_playing():
    player.update()
    # … put other periodic work here …
    time.sleep_ms(1)


# ---------------------------------------------------------------------------
# 3. Random tiny set — good for memory-constrained devices
# ---------------------------------------------------------------------------
player.play_random_blocking(RTTTL_MELODIES_TINY)


# ---------------------------------------------------------------------------
# 4. Looping a melody three times
# ---------------------------------------------------------------------------
from rtttl.melodies import RTTTL_MELODIES

nokia = RTTTL_MELODIES[21]

# Manually inject l=3 into the header section
nokia_3x = nokia.replace("Nokia:", "Nokia:l=3,", 1)
player.play_blocking(nokia_3x)


# ---------------------------------------------------------------------------
# 5. Staccato style
# ---------------------------------------------------------------------------
from rtttl import STYLE_STACCATO

staccato_player = PlayRtttl(pin=BUZZER_PIN, style_divisor=STYLE_STACCATO)
staccato_player.play_blocking(RTTTL_MELODIES[5])  # Muppets, staccato

