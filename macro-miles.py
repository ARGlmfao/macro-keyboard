import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
import json
import os
import threading
import time
import keyboard  # pip install keyboard
import serial
import serial.tools.list_ports

# ----------------- CONFIG -----------------
CONFIG_FILE = os.path.join(os.path.expanduser("~"), "Documents", "pico_macro_profiles.json")
BUTTON_LAYOUT = [
    ["GP1", "GP16", "GP12"],
    ["GP2", "GP10", "GP15"],
    ["GP0", "GP9",  "GP14"]
]

# ----------------- GLOBALS -----------------
profiles = {}
current_profile = None
serial_thread_running = False
USE_LOCK_MODE = True
BUTTON_DELAY = 0.5
button_pressed_state = {}
ser = None
port = None

# ----------------- LOAD PROFILES -----------------
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        profiles = json.load(f)

# ----------------- SERIAL -----------------
def find_pico():
    global ser, port
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if "CircuitPython" in p.description or "USB Serial" in p.description:
            port = p.device
            try:
                ser = serial.Serial(port, 115200, timeout=0.1)
                return True
            except:
                ser = None
    return False

def serial_loop():
    global serial_thread_running
    serial_thread_running = True
    last_time = {}
    for row in BUTTON_LAYOUT:
        for btn in row:
            last_time[btn] = 0

    while serial_thread_running:
        if ser and ser.in_waiting:
            try:
                data = ser.readline().decode().strip()
                # Expected format: GPx_PRESSED / GPx_NOT
                for btn in [b for row in BUTTON_LAYOUT for b in row]:
                    if data == f"{btn}_PRESSED":
                        if USE_LOCK_MODE:
                            if not button_pressed_state.get(btn, False):
                                execute_action(btn)
                                button_pressed_state[btn] = True
                        else:
                            if time.time() - last_time[btn] >= BUTTON_DELAY:
                                execute_action(btn)
                                last_time[btn] = time.time()
                    elif data == f"{btn}_NOT":
                        button_pressed_state[btn] = False
            except:
                pass
        time.sleep(0.05)

# ----------------- GUI -----------------
root = tk.Tk()
root.title("🔥 Pico Macro Manager 🔥")
root.configure(bg="#1e1e1e")

# ----------------- PROFILE MANAGEMENT -----------------
def save_profiles():
    with open(CONFIG_FILE, "w") as f:
        json.dump(profiles, f, indent=4)
    update_button_colors()

def select_profile(name):
    global current_profile
    current_profile = name
    profile_label.config(text=f"Profile: {current_profile}")
    update_button_colors()

def create_profile():
    name = simpledialog.askstring("Create Profile", "Enter profile name:")
    if not name or name in profiles:
        return
    profiles[name] = {}
    save_profiles()
    select_profile(name)
    update_dropdown()

def delete_profile():
    global current_profile
    if not current_profile:
        return
    if messagebox.askyesno("Delete Profile", f"Delete {current_profile}?"):
        profiles.pop(current_profile)
        current_profile = None
        profile_label.config(text="No Profile")
        save_profiles()
        update_dropdown()

def update_dropdown():
    menu = profile_menu["menu"]
    menu.delete(0, "end")
    for name in profiles.keys():
        menu.add_command(label=name, command=lambda n=name: select_profile(n))

# ----------------- BUTTON ACTION CONFIG -----------------
def configure_button(btn_id):
    if not current_profile:
        messagebox.showwarning("No Profile", "Select a profile first!")
        return

    def save_action(action_type, action_value):
        profiles[current_profile][btn_id] = {"action_type": action_type, "action": action_value}
        save_profiles()
        config_win.destroy()

    config_win = tk.Toplevel(root)
    config_win.title(f"Configure {btn_id}")
    config_win.geometry("300x200")
    config_win.configure(bg="#2c2c2c")

    tk.Label(config_win, text=f"Set action for {btn_id}:", bg="#2c2c2c", fg="white").pack(pady=5)

    # Text
    def set_text():
        text = simpledialog.askstring("Text", "Enter text to type:")
        if text: save_action("text", text)

    tk.Button(config_win, text="Text", command=set_text).pack(pady=3)

    # Shortcut
    def set_shortcut():
        num_keys = simpledialog.askinteger("Shortcut", "Number of keys (1-5):", minvalue=1, maxvalue=5)
        if not num_keys: return
        keys = []
        for i in range(num_keys):
            k = simpledialog.askstring("Shortcut", f"Key {i+1} of {num_keys}:")
            if not k: return
            keys.append(k)
        save_action("shortcut", keys)

    tk.Button(config_win, text="Shortcut", command=set_shortcut).pack(pady=3)

    # Program
    def set_program():
        path = filedialog.askopenfilename(title="Select Program")
        if path: save_action("program", path)

    tk.Button(config_win, text="Program", command=set_program).pack(pady=3)

# ----------------- BUTTON EXECUTE -----------------
def execute_action(btn_id):
    if not current_profile:
        return
    action = profiles[current_profile].get(btn_id)
    if not action:
        return
    typ = action["action_type"]
    val = action["action"]
    try:
        if typ == "text":
            keyboard.write(val)
        elif typ == "shortcut":
            combo = "+".join(val)
            keyboard.send(combo)
        elif typ == "program":
            os.startfile(val)
    except Exception as e:
        print("Error executing action:", e)

# ----------------- GUI LAYOUT -----------------
# Profile frame
profile_frame = tk.Frame(root, bg="#2c2c2c")
profile_frame.pack(pady=10)

profile_label = tk.Label(profile_frame, text="No Profile", fg="#00bcd4", bg="#2c2c2c", font=("Arial", 12))
profile_label.pack(side=tk.LEFT, padx=5)

profile_menu_var = tk.StringVar()
profile_menu_var.set("Select Profile")
profile_menu = tk.OptionMenu(profile_frame, profile_menu_var, ())
profile_menu.pack(side=tk.LEFT, padx=5)

tk.Button(profile_frame, text="Create", command=create_profile, bg="#4caf50").pack(side=tk.LEFT, padx=2)
tk.Button(profile_frame, text="Delete", command=delete_profile, bg="#f44336").pack(side=tk.LEFT, padx=2)
update_dropdown()

# Lock/Delay
adv_frame = tk.LabelFrame(root, text="Advanced", bg="#2c2c2c", fg="white")
adv_frame.pack(pady=10, fill="x", padx=10)

lock_var = tk.BooleanVar(value=USE_LOCK_MODE)
tk.Checkbutton(adv_frame, text="Lock Mode", variable=lock_var,
               command=lambda: set_lock(lock_var.get()), bg="#2c2c2c", fg="white").pack(anchor="w", pady=2)

delay_var = tk.DoubleVar(value=BUTTON_DELAY)
tk.Label(adv_frame, text="Delay (sec):", bg="#2c2c2c", fg="white").pack(anchor="w")
tk.Spinbox(adv_frame, from_=0.1, to=5.0, increment=0.1, textvariable=delay_var,
           command=lambda: set_delay(delay_var.get()), width=5).pack(anchor="w")

def set_lock(val):
    global USE_LOCK_MODE
    USE_LOCK_MODE = val

def set_delay(val):
    global BUTTON_DELAY
    BUTTON_DELAY = float(val)

# Button layout
btn_frame = tk.Frame(root, bg="#1e1e1e")
btn_frame.pack(pady=10)

button_widgets = {}
for r, row in enumerate(BUTTON_LAYOUT):
    for c, btn_id in enumerate(row):
        b = tk.Button(btn_frame, text=btn_id, width=10, height=4,
                      bg="#444", fg="white", command=lambda id=btn_id: configure_button(id))
        b.grid(row=r, column=c, padx=5, pady=5)
        button_widgets[btn_id] = b

def update_button_colors():
    if not current_profile:
        for b in button_widgets.values():
            b.config(bg="#444")
        return
    for btn_id, btn in button_widgets.items():
        if btn_id in profiles[current_profile]:
            btn.config(bg="#2196f3")
        else:
            btn.config(bg="#444")

update_button_colors()

# ----------------- INIT SERIAL THREAD -----------------
if find_pico():
    t = threading.Thread(target=serial_loop, daemon=True)
    t.start()
else:
    messagebox.showwarning("Pico", "Pico not detected")

# ----------------- MAIN LOOP -----------------
root.mainloop()

