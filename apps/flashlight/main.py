menu_name = "Flashlight"

from zerophone_hw import RGB_LED

led = None
state = False
context = None

def init_app(i, o):
    global led
    led = RGB_LED()

def set_context(c):
    global context
    context = c
    context.register_action("flashlight_toggle", callback, get_state_message, description="Flashlight toggle")

def get_state_message():
    if state:
        return "Flashlight on"
    else:
        return "Flashlight off"

def callback():
    global state
    if not state:
        led.set_color("white")
        state = True
    else:
        led.set_color("none")
        state = False
