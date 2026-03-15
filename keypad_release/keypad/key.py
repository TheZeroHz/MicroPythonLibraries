"""
@file key.py
@version 1.0
@author Mark Stanley (original C++ library)
@author zerohz (MicroPython port)
@description
| Key class provides an abstract definition of a key or button
| and was initially designed to be used in conjunction with a
| state-machine.
| 
| MicroPython port of the Arduino Keypad library.
#
@license
| This library is free software; you can redistribute it and/or
| modify it under the terms of the GNU Lesser General Public
| License as published by the Free Software Foundation; version
| 2.1 of the License.
|
| This library is distributed in the hope that it will be useful,
| but WITHOUT ANY WARRANTY; without even the implied warranty of
| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
| Lesser General Public License for more details.
|
| You should have received a copy of the GNU Lesser General Public
| License along with this library; if not, write to the Free Software
| Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
"""

# Key states
IDLE = 0
PRESSED = 1
HOLD = 2
RELEASED = 3

NO_KEY = '\0'

OPEN = 0
CLOSED = 1


class Key:
    """Key class provides an abstract definition of a key or button."""
    
    def __init__(self, userKeyChar=None):
        """
        Initialize a Key object.
        
        Args:
            userKeyChar: Optional character for the key. If None, creates an empty key.
        """
        if userKeyChar is None:
            self.kchar = NO_KEY
            self.kcode = -1
        else:
            self.kchar = userKeyChar
            self.kcode = -1
        self.kstate = IDLE
        self.stateChanged = False
    
    def key_update(self, userKeyChar, userState, userStatus):
        """
        Update the key with new values.
        
        Args:
            userKeyChar: Character for the key
            userState: KeyState (IDLE, PRESSED, HOLD, RELEASED)
            userStatus: Boolean indicating if state changed
        """
        self.kchar = userKeyChar
        self.kstate = userState
        self.stateChanged = userStatus

