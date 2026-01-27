Macro Keyboard – README
Overview

This project is a custom macro keyboard I built using a Raspberry Pi Pico running CircuitPython, paired with a PC-side software application.
The system supports multiple profiles, allowing the same physical buttons to perform different actions depending on the active profile.
----------------------------
**Setup Summary**

1.Flash CircuitPython onto the Raspberry Pi Pico

2.Copy boot.py (USB CDC enabled) and code.py to the Pico

3.Wire buttons to GPIO pins and GND

4.code the gui.py to your pc/laptop

6.Run the gui.py using IDE or directly run the macro-miles.exe

7.Select the correct COM port

8.Create or load a profile and assign macros

**System Architecture**
Hardware:

  •Raspberry Pi Pico
  •Physical push buttons connected to GPIO pins
  •Buttons configured using internal pull-up resistors
- Each button press is detected reliably and sent to the PC.

**Firmware (Pico – CircuitPython)**

  •Detects button presses
  •Sends button identifiers to the PC via USB CDC (Serial)
  •Does not store or execute macros
- The Pico acts only as an input device.

**PC Software**

  •Python-based GUI application
  •Communicates with the Pico over USB Serial
  - Handles:

      •Profile creation and switching
      •Macro assignment
      •Saving/loading configurations (JSON)
      •Executing macros on the host computer

**Profiles**

Profiles allow different macro mappings for the same buttons.

Examples:

  •Gaming profile
  •Coding profile
  •Productivity profile
- Switching profiles instantly changes keyboard behavior without reflashing the Pico.

**Configuration**

  •Profiles are stored as JSON files
  •Each profile maps button IDs to macros
  •Files are human-readable and easy to modify


**Notes**

•All macro logic runs on the PC
•The Pico remains profile-agnostic
•Profiles can be edited without reconnecting hardware
