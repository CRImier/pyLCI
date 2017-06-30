menu_name = "Phone" 

from subprocess import call as os_call

from ui import Refresher, Menu, Printer, format_for_screen as ffs
from ui.experimental import NumberKeypadInputLayer

from phone import Modem, ATError

i = None 
o = None 
modem = None

def answer():
    #No context switching as for now, so all we can do is 
    #answer call is there's an active one
    try:
        modem.answer()
    except ATError:
        pass

def hangup():
    try:
        modem.hangup()
    except ATError:
        pass

def call(number):
    Printer("Calling {}".format(number), i, o, 0)
    try:
        modem.call(number)
    except ATError as e:
        Printer(ffs("Modem fail! "+repr(e), o.cols), i, o, 0)
 
def call_view():
    keymap = {"KEY_ANSWER":[call]}
    NumberKeypadInputLayer(i, o, "Call number", keymap, name="Phone call layer").activate()

def status_refresher():
    Refresher(calling_status, i, o).activate()

def check_modem_connection():
    global modem
    if modem is not None: return True
    Printer(ffs("Connecting to modem", o.cols), i, o)
    try:
        modem = Modem()
        modem.init_modem()
        modem.start_monitoring()
        return True
    except ValueError as e:
        print(repr(e))
        Printer(ffs("Modem connection failed", o.cols), i, o)
        modem.stop_monitoring()
        modem.deinit_modem()
        modem = None
        return False

def init_app(input, output):
    global i, o
    i = input; o = output 
    i.set_nonmaskable_callback("KEY_ANSWER", answer)
    i.set_nonmaskable_callback("KEY_HANGUP", hangup)
    #This not good enough - either make the systemctl library system-wide or add more checks
    try:
        os_call(["systemctl", "stop", "serial-getty@ttyAMA0.service"])
    except Exception as e:
        print(repr(e))
        #import pdb;pdb.set_trace()
    check_modem_connection()

def callback():
    if not check_modem_connection():
        Printer(ffs("Modem connection failed", o.cols), i, o)
        return
    contents = [["Status", status_refresher],
                ["Call", call_view]]
    Menu(contents, i, o).activate()
