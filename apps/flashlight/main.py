menu_name = "Flashlight"

from zerophone_hw import RGB_LED

led = None
state = False

def init_app(i, o):
    global led
    led = RGB_LED()

def callback():
    global state
    if not state:
        led.set_color("white")
        state = True
    else:
        led.set_color("none")
        state = False
