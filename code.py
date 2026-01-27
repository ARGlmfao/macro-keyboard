import board
import digitalio
import time

# ----------------- BUTTON SETUP -----------------
buttons = {
    "GP1": digitalio.DigitalInOut(board.GP1),
    "GP16": digitalio.DigitalInOut(board.GP16),
    "GP12": digitalio.DigitalInOut(board.GP12),
    "GP2": digitalio.DigitalInOut(board.GP2),
    "GP10": digitalio.DigitalInOut(board.GP10),
    "GP15": digitalio.DigitalInOut(board.GP15),
    "GP0": digitalio.DigitalInOut(board.GP0),
    "GP9": digitalio.DigitalInOut(board.GP9),
    "GP14": digitalio.DigitalInOut(board.GP14),
}

# Set direction and pull-ups
for btn in buttons.values():
    btn.direction = digitalio.Direction.INPUT
    btn.pull = digitalio.Pull.UP

# ----------------- STATE TRACKING -----------------
last_state = {btn_id: True for btn_id in buttons}  # True = not pressed, False = pressed

# ----------------- LOOP -----------------
while True:
    for btn_id, btn in buttons.items():
        if btn.value != last_state[btn_id]:
            if not btn.value:
                print(f"{btn_id}_PRESSED")
            else:
                print(f"{btn_id}_NOT")
            last_state[btn_id] = btn.value
    time.sleep(0.05)  # 50ms debounce


