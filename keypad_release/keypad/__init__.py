"""
Keypad library for MicroPython
A port of the Arduino Keypad library for matrix keypads.
"""

# Import key module first (it has no dependencies on keypad)
import keypad.key as _key_mod

# Then import keypad module (which depends on key)
import keypad.keypad as _keypad_mod

# Export the classes and constants
Keypad = _keypad_mod.Keypad
Key = _key_mod.Key
IDLE = _key_mod.IDLE
PRESSED = _key_mod.PRESSED
HOLD = _key_mod.HOLD
RELEASED = _key_mod.RELEASED
NO_KEY = _key_mod.NO_KEY

__all__ = ['Keypad', 'Key', 'IDLE', 'PRESSED', 'HOLD', 'RELEASED', 'NO_KEY']
