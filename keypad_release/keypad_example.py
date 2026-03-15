from keypad import Keypad, PRESSED, HOLD, RELEASED

ROWS = 4
COLS = 4
keys = ['1', '2', '3', 'a',
        '4', '5', '6', 'b',
        '7', '8', '9', 'c',
        '*', '0', '#', 'd']
rowPins = [0, 1, 2, 3]
colPins = [4, 5, 14, 15]

keypad = Keypad(keys, rowPins, colPins, ROWS, COLS)

while True:
    if keypad.getKeys():
        for i in range(keypad.numKeys()):
            key = keypad.key[i]
            if key.kchar != '\0' and key.stateChanged:
                if key.kstate == PRESSED:
                    print(f"Key {key.kchar} pressed")
                elif key.kstate == HOLD:
                    print(f"Key {key.kchar} held")
                elif key.kstate == RELEASED:
                    print(f"Key {key.kchar} released")