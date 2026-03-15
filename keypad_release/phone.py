from keypad import Keypad, PRESSED, HOLD, RELEASED
import _thread
import time
from machine import Pin, PWM, I2C
from lcd import I2cLcd
from gsm import Phone
from rtttl import PlayRtttl
from rtttl.melodies import RTTTL_MELODIES

# =========================================================
# 0) GSM SETUP (SIM800L via gsm.Phone)
# =========================================================
# UART1 on Pico: tx=GP4, rx=GP5 (as your example)
gsm = Phone(uart_id=1, tx_pin=4, rx_pin=5, baud=9600)

# =========================================================
# 1) KEYPAD SETUP
# =========================================================
ROWS = 4
COLS = 4
keys = ['1', '2', '3', 'a',
        '4', '5', '6', 'b',
        '7', '8', '9', 'c',
        '*', '0', '#', 'd']

rowPins = [0, 1, 2, 3]
colPins = [12, 13, 14, 15]   # ✅ no conflict with UART pins 4/5

keypad = Keypad(keys, rowPins, colPins, ROWS, COLS)

# =========================================================
# 2) BUZZER SETUP (PWM - passive buzzer)
# =========================================================
BUZZER_PIN = 28
BUZZ_FREQ = 2200
BUZZ_DUTY = 25535
DEFAULT_BEEP_MS = 40

buzzer = PWM(Pin(BUZZER_PIN))
buzzer.duty_u16(0)

def do_beep(duration_ms=DEFAULT_BEEP_MS):
    buzzer.freq(BUZZ_FREQ)
    buzzer.duty_u16(BUZZ_DUTY)
    time.sleep_ms(duration_ms)
    buzzer.duty_u16(0)

# =========================================================
# 2.5) RTTL RINGTONE PLAYER SETUP
# =========================================================
# Use Nokia ringtone (index 21) as default, or you can change it
RINGTONE_MELODY = RTTTL_MELODIES[21]  # Nokia ringtone
rtttl_player = PlayRtttl(pin=BUZZER_PIN)

# =========================================================
# 3) LCD SETUP (I2C 16x2)
# =========================================================
# If needed, set pins explicitly:
# i2c = I2C(1, sda=Pin(6), scl=Pin(7), freq=100000)
i2c = I2C(1, freq=100000)

LCD_ADDR = 0x27
lcd = I2cLcd(i2c, LCD_ADDR, 2, 16)

def lcd_line(row, text):
    lcd.move_to(0, row)
    lcd.putstr(" " * 16)
    lcd.move_to(0, row)
    lcd.putstr(text[:16])

def show_status(status):
    lcd_line(0, status)

def show_dial(buf):
    lcd_line(1, buf[-16:])

# Boot screen
lcd.clear()
lcd_line(0, "21 February!")
lcd_line(1, "Vasha Dibosh")
time.sleep_ms(900)
lcd.clear()

# =========================================================
# 4) BEEP THREAD (EVENT QUEUE)
# =========================================================
_beep_count = 0
_lock = _thread.allocate_lock()

def request_beep(n=1):
    global _beep_count
    with _lock:
        _beep_count += n

def beep_worker():
    global _beep_count
    while True:
        n = 0
        with _lock:
            if _beep_count > 0:
                n = _beep_count
                _beep_count = 0

        if n:
            for _ in range(min(n, 3)):
                do_beep(DEFAULT_BEEP_MS)
                time.sleep_ms(25)
        else:
            time.sleep_ms(5)

_thread.start_new_thread(beep_worker, ())

# =========================================================
# 5) PHONE LOGIC + GSM
# =========================================================
dial = ""
call_state = "READY"   # READY, CALLING, IN_CALL, INCOMING
incoming_number = ""
ringtone_playing = False

def gsm_init_status():
    # Quick check like your example
    if gsm.is_ok():
        show_status("GSM ONLINE")
        time.sleep_ms(500)

        try:
            batt = gsm.battery_percentage()
            show_status("BAT {}%".format(batt))
            time.sleep_ms(500)
        except:
            pass

        show_status("READY")
    else:
        show_status("GSM OFFLINE")
        time.sleep_ms(800)
        show_status("READY")

def start_call():
    global call_state, dial
    if len(dial) == 0:
        show_status("NO NUMBER")
        time.sleep_ms(400)
        show_status("READY")
        return

    if not gsm.is_ok():
        show_status("NO GSM")
        time.sleep_ms(500)
        show_status("READY")
        return

    call_state = "CALLING"
    show_status("CALLING...")
    try:
        gsm.call(dial)
    except Exception as e:
        print("gsm.call error:", e)
        show_status("CALL FAIL")
        time.sleep_ms(500)
        call_state = "READY"
        show_status("READY")

def accept_call():
    # If your gsm library supports accept, usually it's ATA.
    # Some libraries have gsm.accept_call() / gsm.answer()
    # We'll try common names safely.
    global call_state, ringtone_playing
    show_status("ACCEPTING..")
    
    # Stop ringtone if playing
    if ringtone_playing:
        rtttl_player.stop()
        ringtone_playing = False
    
    ok = False
    for fn in ("accept_call", "answer", "pickup", "ata"):
        if hasattr(gsm, fn):
            try:
                getattr(gsm, fn)()
                ok = True
                break
            except Exception as e:
                print(fn, "error:", e)

    call_state = "IN CALL" if ok else call_state
    show_status("IN CALL" if ok else "NO ACCEPT")
    time.sleep_ms(400)
    if not ok:
        show_status(call_state)

def hangup_call():
    global call_state, ringtone_playing, incoming_number
    show_status("HANG UP")
    
    # Stop ringtone if playing
    if ringtone_playing:
        rtttl_player.stop()
        ringtone_playing = False
    
    try:
        # your example uses cut_call()
        gsm.cut_call()
    except Exception as e:
        print("gsm.cut_call error:", e)
    call_state = "READY"
    incoming_number = ""
    time.sleep_ms(250)
    show_status("READY")
    show_dial("")

def backspace():
    global dial
    dial = dial[:-1] if len(dial) else dial
    show_dial(dial)

def clear_all():
    global dial
    dial = ""
    show_dial(dial)

def handle_incoming_call(caller_number=""):
    """Handle incoming call - start ringtone and update display"""
    global call_state, ringtone_playing, incoming_number
    
    if call_state != "INCOMING":
        call_state = "INCOMING"
        incoming_number = caller_number if caller_number else "UNKNOWN"
        
        # Display incoming call info
        if caller_number:
            show_status("INCOMING CALL")
            show_dial(caller_number[-16:])  # Show last 16 chars of number
        else:
            show_status("INCOMING CALL")
            show_dial("UNKNOWN")
        
        # Start ringtone (non-blocking, loops until stopped)
        if not ringtone_playing:
            # Start ringtone - will be restarted when it finishes if still incoming
            rtttl_player.start(RINGTONE_MELODY)
            ringtone_playing = True
            print("Incoming call from:", caller_number)

def check_gsm_notifications():
    """Check for GSM notifications (incoming calls, etc.)"""
    global call_state, ringtone_playing
    
    try:
        notification = gsm.loop()
        if notification:
            # Check for incoming call
            if "RING" in notification or "+CLIP" in notification:
                # Try to extract caller number from CLIP (Caller Line Identification Presentation)
                caller_num = ""
                if "+CLIP" in notification:
                    # Format: +CLIP: "+1234567890",129,"",0,"",0
                    try:
                        parts = notification.split('"')
                        if len(parts) > 1:
                            caller_num = parts[1]
                    except:
                        pass
                
                # Only handle if not already in INCOMING state
                if call_state != "INCOMING" and call_state != "IN CALL":
                    handle_incoming_call(caller_num)
            
            # Check if call was answered or ended
            if "NO CARRIER" in notification or "BUSY" in notification:
                if call_state == "CALLING":
                    call_state = "READY"
                    show_status("CALL ENDED")
                    time.sleep_ms(500)
                    show_status("READY")
                    show_dial("")
            
            # Check if call is connected
            if "CONNECT" in notification or "OK" in notification:
                if call_state == "CALLING":
                    call_state = "IN CALL"
                    show_status("IN CALL")
    except Exception as e:
        # Silently handle errors to not spam console
        pass

# Init UI
show_status("BOOT...")
show_dial("")
gsm_init_status()

# =========================================================
# 6) MAIN LOOP
# =========================================================
while True:
    # Update RTTL player if ringtone is playing
    if ringtone_playing:
        # Update player and restart ringtone if it finished and call is still incoming
        if not rtttl_player.update():
            # Ringtone finished, restart if still in INCOMING state
            if call_state == "INCOMING":
                rtttl_player.start(RINGTONE_MELODY)
            else:
                ringtone_playing = False
    
    # Check for GSM notifications (incoming calls, etc.)
    check_gsm_notifications()
    
    if keypad.getKeys():
        for i in range(keypad.numKeys()):
            key = keypad.key[i]
            if key.kchar != '\0' and key.stateChanged:

                if key.kstate == PRESSED:
                    request_beep(1)
                    k = key.kchar
                    print("Key {} pressed".format(k))

                    # --- CONTROL KEYS ---
                    if k == 'a':
                        # CALL / ACCEPT
                        if call_state == "IN CALL":
                            # already in call, ignore
                            pass
                        elif call_state == "INCOMING":
                            # Accept incoming call
                            accept_call()
                        elif call_state == "CALLING":
                            # treat as "accept" (some modules use it to connect),
                            # but mostly no-op. We'll attempt accept anyway.
                            accept_call()
                        else:
                            start_call()

                    elif k == 'b':
                        # CUT / REJECT
                        if call_state == "INCOMING":
                            # Reject incoming call
                            hangup_call()
                        else:
                            # Hang up active call
                            hangup_call()

                    elif k == 'c':
                        # erase one digit
                        if call_state == "READY":
                            backspace()

                    elif k == 'd':
                        # erase all
                        if call_state == "READY":
                            clear_all()

                    else:
                        # --- DIAL KEYS (including * and #) ---
                        if call_state == "READY":
                            dial += k
                            show_dial(dial)

                elif key.kstate == HOLD:
                    print("Key {} held".format(key.kchar))

                elif key.kstate == RELEASED:
                    print("Key {} released".format(key.kchar))

    time.sleep_ms(10)