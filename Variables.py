from Main import threading, tk, vg

# Global variables
listening = threading.Event()
testing = False

# Binding Variables
wheelChocksPlaceVar = tk.StringVar(value='A Button')
wheelChocksRemoveVar = tk.StringVar(value='B Button')
radioCheckVar = tk.StringVar(value='Guide')
groundAirConnectVar = tk.StringVar(value='X Button')
groundAirDisconnectVar = tk.StringVar(value='Y Button')
valueList = ["D-Pad Up", "D-Pad Down", "D-Pad Left", "D-Pad Right", "Start", "Guide",
             "Back", "Left Trigger", "Right Trigger", "Left Shoulder", "Right Shoulder",
             "A Button", "B Button", "X Button", "Y Button"]

# Store the VG values of the bindings
VG_values = {
    "D-Pad Up": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
    "D-Pad Down": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
    "D-Pad Left": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
    "D-Pad Right": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
    "Start": vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
    "Guide": vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE,
    "Back": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
    "Left Trigger": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
    "Right Trigger": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
    "Left Shoulder": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
    "Right Shoulder": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
    "A Button": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
    "B Button": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
    "X Button": vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
    "Y Button":vg.XUSB_BUTTON.XUSB_GAMEPAD_Y
}