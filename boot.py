import usb_cdc
import usb_hid

# Enable USB serial for PC communication
usb_cdc.enable(console=True, data=True)

# Disable HID so it doesn’t auto-spam keyboard
usb_hid.disable()
