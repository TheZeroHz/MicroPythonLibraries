"""
I2C LCD Implementation for PCF8574 Expander
Works with 16x2 and 20x4 displays
"""

from .lcd_api import LcdApi
from machine import I2C
from time import sleep_ms

DEFAULT_I2C_ADDR = 0x27

# Defines shifts or masks for the various LCD lines attached to the PCF8574
MASK_RS = 0x01
MASK_RW = 0x02
MASK_E = 0x04
SHIFT_BACKLIGHT = 3
SHIFT_DATA = 4


class I2cLcd(LcdApi):
    """Implements a character based LCD connected via PCF8574 on I2C.
    
    This class handles communication with LCD displays connected through
    a PCF8574 8-bit I/O expander on an I2C bus.
    
    Attributes:
        i2c: I2C bus object
        i2c_addr: I2C address of the PCF8574 expander
    """

    def __init__(self, i2c, i2c_addr=DEFAULT_I2C_ADDR, num_lines=2, num_columns=16):
        """Initialize I2C LCD display.
        
        Args:
            i2c: I2C object (from machine.I2C)
            i2c_addr: I2C address of PCF8574 (default: 0x27)
            num_lines: Number of lines (2 or 4, default: 2)
            num_columns: Number of columns (16 or 20, default: 16)
            
        Raises:
            Exception: If I2C communication fails during initialization
        """
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        
        print(f"\n[I2C LCD] Initializing...")
        print(f"  Address: 0x{i2c_addr:02x}")
        print(f"  Size: {num_columns}x{num_lines}")
        
        # Initialize the display
        try:
            self.i2c.writeto(self.i2c_addr, bytearray([0]))
            print("  ✓ I2C write successful")
        except Exception as e:
            print(f"  ✗ I2C write failed: {e}")
            raise
        
        sleep_ms(20)  # Allow LCD time to power up
        
        # Send reset 3 times
        print("  - Sending reset sequence...")
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        sleep_ms(5)  # need to delay at least 4.1 msec
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        sleep_ms(1)
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        sleep_ms(1)
        
        # Put LCD into 4 bit mode
        print("  - Setting 4-bit mode...")
        self.hal_write_init_nibble(self.LCD_FUNCTION)
        sleep_ms(1)
        
        # Initialize parent class
        LcdApi.__init__(self, num_lines, num_columns)
        
        # Configure for 2-line mode if needed
        cmd = self.LCD_FUNCTION
        if num_lines > 1:
            cmd |= self.LCD_FUNCTION_2LINES
        self.hal_write_command(cmd)
        
        print("  ✓ Initialization complete!\n")

    def hal_write_init_nibble(self, nibble):
        """Writes an initialization nibble to the LCD.
        
        This is only used during initialization and sends 4-bit data.
        
        Args:
            nibble: 4-bit nibble to write
        """
        byte = ((nibble >> 4) & 0x0f) << SHIFT_DATA
        self.i2c.writeto(self.i2c_addr, bytearray([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte]))

    def hal_backlight_on(self):
        """Turns the backlight on."""
        self.i2c.writeto(self.i2c_addr, bytearray([1 << SHIFT_BACKLIGHT]))

    def hal_backlight_off(self):
        """Turns the backlight off."""
        self.i2c.writeto(self.i2c_addr, bytearray([0]))

    def hal_write_command(self, cmd):
        """Writes a command to the LCD.
        
        Data is latched on the falling edge of E (enable pin).
        Commands are sent in 4-bit mode (two nibbles).
        
        Args:
            cmd: Command byte to write
        """
        # Send high nibble
        byte = (
            (self.backlight << SHIFT_BACKLIGHT)
            | (((cmd >> 4) & 0x0f) << SHIFT_DATA)
        )
        self.i2c.writeto(self.i2c_addr, bytearray([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte]))
        
        # Send low nibble
        byte = (
            (self.backlight << SHIFT_BACKLIGHT)
            | ((cmd & 0x0f) << SHIFT_DATA)
        )
        self.i2c.writeto(self.i2c_addr, bytearray([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte]))
        
        if cmd <= 3:
            # The home and clear commands require a worst case delay of 4.1 msec
            sleep_ms(5)

    def hal_write_data(self, data):
        """Write data to the LCD.
        
        Data is sent in 4-bit mode (two nibbles) with RS pin set high.
        
        Args:
            data: Data byte to write (usually a character code)
        """
        # Send high nibble
        byte = (
            MASK_RS
            | (self.backlight << SHIFT_BACKLIGHT)
            | (((data >> 4) & 0x0f) << SHIFT_DATA)
        )
        self.i2c.writeto(self.i2c_addr, bytearray([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte]))
        
        # Send low nibble
        byte = (
            MASK_RS
            | (self.backlight << SHIFT_BACKLIGHT)
            | ((data & 0x0f) << SHIFT_DATA)
        )
        self.i2c.writeto(self.i2c_addr, bytearray([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte]))
