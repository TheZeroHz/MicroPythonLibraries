from machine import I2C
from lcd import I2cLcd

# Initialize I2C bus
i2c = I2C(1, freq=100000)

# Create LCD display (16x2 at default address 0x27)
lcd = I2cLcd(i2c, 0x27, 2, 16)

# Display text
lcd.putstr("21 February!")

# Move cursor and display more text
lcd.move_to(0, 1)
lcd.putstr("Vasha Dibosh")