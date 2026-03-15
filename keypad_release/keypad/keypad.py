"""
@file keypad.py
@version 3.1
@author Mark Stanley, Alexander Brevig (original C++ library)
@author zerohz (MicroPython port)
@description
| This library provides a simple interface for using matrix
| keypads. It supports multiple keypresses while maintaining
| backwards compatibility with the old single key library.
| It also supports user selectable pins and definable keymaps.
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

try:
    from machine import Pin
    import time
except ImportError:
    raise ImportError("This library requires MicroPython with machine module")

# Import from the same package - try multiple methods for MicroPython compatibility
# Try importing key module - order matters for package initialization
try:
    # Method 1: Try relative import first (works when imported as package)
    from .key import Key, IDLE, PRESSED, HOLD, RELEASED, NO_KEY, OPEN, CLOSED
except ImportError:
    try:
        # Method 2: Import from package (works when package is initialized)
        from keypad.key import Key, IDLE, PRESSED, HOLD, RELEASED, NO_KEY, OPEN, CLOSED
    except ImportError:
        try:
            # Method 3: Try importing via sys.modules (if already loaded)
            import sys
            if 'keypad.key' in sys.modules:
                _k = sys.modules['keypad.key']
                Key = _k.Key
                IDLE = _k.IDLE
                PRESSED = _k.PRESSED
                HOLD = _k.HOLD
                RELEASED = _k.RELEASED
                NO_KEY = _k.NO_KEY
                OPEN = _k.OPEN
                CLOSED = _k.CLOSED
            else:
                # Method 4: Direct import (if key.py is on path)
                from key import Key, IDLE, PRESSED, HOLD, RELEASED, NO_KEY, OPEN, CLOSED
        except ImportError as e:
            raise ImportError(f"Failed to import key module: {e}")

LIST_MAX = 10  # Max number of keys on the active list
MAPSIZE = 10   # MAPSIZE is the number of rows (times 16 columns)


class Keypad:
    """
    Keypad class for matrix keypad support in MicroPython.
    Supports multiple keypresses and state machine-based debouncing.
    """
    
    def __init__(self, userKeymap, rowPins, colPins, numRows, numCols):
        """
        Initialize the Keypad.
        
        Args:
            userKeymap: List or string of characters representing the keypad layout
                       (row-major order: row0_col0, row0_col1, ..., row1_col0, ...)
            rowPins: List of pin numbers for rows
            colPins: List of pin numbers for columns
            numRows: Number of rows in the keypad
            numCols: Number of columns in the keypad
        """
        self.rowPins = rowPins
        self.columnPins = colPins
        self.sizeKpd = {'rows': numRows, 'columns': numCols}
        
        # Convert keymap to list if it's a string
        if isinstance(userKeymap, str):
            self.keymap = list(userKeymap)
        else:
            self.keymap = userKeymap
        
        # Validate keymap size
        expectedSize = numRows * numCols
        if len(self.keymap) != expectedSize:
            raise ValueError(f"Keymap size mismatch: expected {expectedSize} keys (rows={numRows} * cols={numCols}), got {len(self.keymap)}")
        
        # Initialize pin objects
        self._rowPinObjects = []
        self._colPinObjects = []
        
        # Initialize row pins as inputs with pull-up
        for r in range(numRows):
            pin = Pin(rowPins[r], Pin.IN, Pin.PULL_UP)
            self._rowPinObjects.append(pin)
        
        # Initialize column pins (will be set as outputs during scanning)
        for c in range(numCols):
            pin = Pin(colPins[c], Pin.OUT)
            pin.value(1)  # Set high initially
            self._colPinObjects.append(pin)
        
        # Initialize key tracking
        self.bitMap = [0] * MAPSIZE  # 10 row x 16 column array of bits
        self.key = [Key() for _ in range(LIST_MAX)]
        self.holdTimer = 0
        
        # Configuration
        self.debounceTime = 10  # milliseconds
        self.holdTime = 500     # milliseconds
        self.startTime = 0
        self.single_key = False
        self.keypadEventListener = None
    
    def begin(self, userKeymap):
        """
        Let the user define a keymap - assume the same row/column count as defined in constructor.
        
        Args:
            userKeymap: List or string of characters representing the keypad layout
        """
        if isinstance(userKeymap, str):
            self.keymap = list(userKeymap)
        else:
            self.keymap = userKeymap
    
    def getKey(self):
        """
        Returns a single key only. Retained for backwards compatibility.
        
        Returns:
            Character of the pressed key, or NO_KEY if no key pressed
        """
        self.single_key = True
        
        if self.getKeys() and self.key[0].stateChanged and (self.key[0].kstate == PRESSED):
            result = self.key[0].kchar
            self.single_key = False
            # Return NO_KEY if result is empty or None
            if not result or result == NO_KEY:
                return NO_KEY
            return result
        
        self.single_key = False
        return NO_KEY
    
    def getKeys(self):
        """
        Populate the key list.
        
        Returns:
            True if any key activity occurred, False otherwise
        """
        keyActivity = False
        
        # Limit how often the keypad is scanned. This makes the loop() run 10 times as fast.
        currentTime = time.ticks_ms()
        if time.ticks_diff(currentTime, self.startTime) > self.debounceTime:
            self.scanKeys()
            keyActivity = self.updateList()
            self.startTime = currentTime
        
        return keyActivity
    
    def scanKeys(self):
        """
        Private: Hardware scan
        Scans the keypad matrix to detect which keys are pressed.
        """
        # Re-initialize the row pins. Allows sharing these pins with other hardware.
        for r in range(self.sizeKpd['rows']):
            self._rowPinObjects[r].init(Pin.IN, Pin.PULL_UP)
        
        # bitMap stores ALL the keys that are being pressed.
        for c in range(self.sizeKpd['columns']):
            # Set column pin as output and drive LOW
            self._colPinObjects[c].init(Pin.OUT)
            self._colPinObjects[c].value(0)
            
            # Read all row pins
            for r in range(self.sizeKpd['rows']):
                # keypress is active low so invert to high
                bitValue = not self._rowPinObjects[r].value()
                # Set bit in bitmap
                if bitValue:
                    self.bitMap[r] |= (1 << c)
                else:
                    self.bitMap[r] &= ~(1 << c)
            
            # Set pin to high impedance input. Effectively ends column pulse.
            self._colPinObjects[c].value(1)
            self._colPinObjects[c].init(Pin.IN)
    
    def updateList(self):
        """
        Manage the list without rearranging the keys.
        Returns true if any keys on the list changed state.
        """
        anyActivity = False
        
        # Delete any IDLE keys
        for i in range(LIST_MAX):
            if self.key[i].kstate == IDLE:
                self.key[i].kchar = NO_KEY
                self.key[i].kcode = -1
                self.key[i].stateChanged = False
        
        # Add new keys to empty slots in the key list.
        for r in range(self.sizeKpd['rows']):
            for c in range(self.sizeKpd['columns']):
                button = bool(self.bitMap[r] & (1 << c))
                keyIndex = r * self.sizeKpd['columns'] + c
                # Bounds check for keymap
                if keyIndex >= len(self.keymap):
                    continue  # Skip if keymap index is out of bounds
                keyChar = self.keymap[keyIndex]
                keyCode = keyIndex
                idx = self.findInList(keyCode)
                
                # Key is already on the list so set its next state.
                if idx > -1:
                    self.nextKeyState(idx, button)
                
                # Key is NOT on the list so add it.
                if (idx == -1) and button:
                    # Skip if keyChar is empty or None
                    if not keyChar or keyChar == NO_KEY:
                        continue
                    for i in range(LIST_MAX):
                        if self.key[i].kchar == NO_KEY:  # Find an empty slot or don't add key to list.
                            self.key[i].kchar = keyChar
                            self.key[i].kcode = keyCode
                            self.key[i].kstate = IDLE  # Keys NOT on the list have an initial state of IDLE.
                            self.nextKeyState(i, button)
                            break  # Don't fill all the empty slots with the same key.
        
        # Report if the user changed the state of any key.
        for i in range(LIST_MAX):
            if self.key[i].stateChanged:
                anyActivity = True
        
        return anyActivity
    
    def nextKeyState(self, idx, button):
        """
        Private: This function is a state machine but is also used for debouncing the keys.
        
        Args:
            idx: Index into the key list
            button: Boolean indicating if button is pressed (CLOSED) or not (OPEN)
        """
        self.key[idx].stateChanged = False
        
        currentTime = time.ticks_ms()
        
        if self.key[idx].kstate == IDLE:
            if button == CLOSED:
                self.transitionTo(idx, PRESSED)
                self.holdTimer = currentTime  # Get ready for next HOLD state.
        elif self.key[idx].kstate == PRESSED:
            if time.ticks_diff(currentTime, self.holdTimer) > self.holdTime:  # Waiting for a key HOLD...
                self.transitionTo(idx, HOLD)
            elif button == OPEN:  # or for a key to be RELEASED.
                self.transitionTo(idx, RELEASED)
        elif self.key[idx].kstate == HOLD:
            if button == OPEN:
                self.transitionTo(idx, RELEASED)
        elif self.key[idx].kstate == RELEASED:
            self.transitionTo(idx, IDLE)
    
    def isPressed(self, keyChar):
        """
        Check if a specific key character is currently pressed.
        
        Args:
            keyChar: Character to check
            
        Returns:
            True if the key is pressed and state changed, False otherwise
        """
        for i in range(LIST_MAX):
            if self.key[i].kchar == keyChar:
                if (self.key[i].kstate == PRESSED) and self.key[i].stateChanged:
                    return True
        return False  # Not pressed.
    
    def findInList(self, keyCharOrCode):
        """
        Search by character or code for a key in the list of active keys.
        Returns -1 if not found or the index into the list of active keys.
        
        Args:
            keyCharOrCode: Character or integer key code to search for
            
        Returns:
            Index in the key list, or -1 if not found
        """
        for i in range(LIST_MAX):
            if isinstance(keyCharOrCode, str):
                if self.key[i].kchar == keyCharOrCode:
                    return i
            else:
                if self.key[i].kcode == keyCharOrCode:
                    return i
        return -1
    
    def waitForKey(self):
        """
        Block until a key is pressed, then return it.
        
        Returns:
            Character of the pressed key
        """
        waitKey = NO_KEY
        while (waitKey := self.getKey()) == NO_KEY:
            pass  # Block everything while waiting for a keypress.
        return waitKey
    
    def getState(self):
        """
        Backwards compatibility function.
        Returns the state of the first key in the list.
        
        Returns:
            KeyState of the first key
        """
        return self.key[0].kstate
    
    def keyStateChanged(self):
        """
        The end user can test for any changes in state before deciding
        if any variables, etc. needs to be updated in their code.
        
        Returns:
            True if the first key's state changed, False otherwise
        """
        return self.key[0].stateChanged
    
    def numKeys(self):
        """
        The number of keys on the key list.
        
        Returns:
            Number of keys (LIST_MAX)
        """
        return LIST_MAX
    
    def setDebounceTime(self, debounce):
        """
        Set the debounce time in milliseconds.
        Minimum debounceTime is 1 mS. Any lower *will* slow down the loop().
        
        Args:
            debounce: Debounce time in milliseconds
        """
        self.debounceTime = max(1, debounce)
    
    def setHoldTime(self, hold):
        """
        Set the hold time in milliseconds.
        This is the time a key must be held before entering HOLD state.
        
        Args:
            hold: Hold time in milliseconds
        """
        self.holdTime = hold
    
    def addEventListener(self, listener):
        """
        Add an event listener function that will be called when key states change.
        
        Args:
            listener: Function that takes a character argument
        """
        self.keypadEventListener = listener
    
    def transitionTo(self, idx, nextState):
        """
        Transition a key to a new state and trigger event listener if set.
        
        Args:
            idx: Index into the key list
            nextState: Next KeyState (IDLE, PRESSED, HOLD, RELEASED)
        """
        self.key[idx].kstate = nextState
        self.key[idx].stateChanged = True
        
        # Sketch used the getKey() function.
        # Calls keypadEventListener only when the first key in slot 0 changes state.
        if self.single_key:
            if (self.keypadEventListener is not None) and (idx == 0):
                self.keypadEventListener(self.key[0].kchar)
        # Sketch used the getKeys() function.
        # Calls keypadEventListener on any key that changes state.
        else:
            if self.keypadEventListener is not None:
                self.keypadEventListener(self.key[idx].kchar)

