"""
MicroPython LCD Display Library
A modular library for character LCD displays via I2C

This package provides easy-to-use classes for controlling LCD displays
connected via PCF8574 I2C expanders on MicroPython devices.

Example:
    from machine import I2C
    from micropython_lcd import I2cLcd
    
    i2c = I2C(1, freq=100000)
    lcd = I2cLcd(i2c, 0x27, 2, 16)
    lcd.putstr("Hello World!")
"""

from .lcd_api import LcdApi
from .i2c_lcd import I2cLcd

__version__ = "1.0.0"
__author__ = "Your Name"
__all__ = ["LcdApi", "I2cLcd"]
