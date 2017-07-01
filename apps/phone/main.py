menu_name = "Phone" 

from subprocess import call as os_call
from threading import Thread, Event

from ui import Refresher, Menu, Printer, format_for_screen as ffs
from ui.experimental import NumberKeypadInputLayer

from phone import Phone, Modem, ATError

i = None
o = None
phone = None
modem = None

connecting = Event()

def answer():
    #No context switching as for now, so all we can do is 
    #answer call is there's an active one
    try:
        phone.answer()
    except ATError:
        pass

def hangup():
    try:
        phone.hangup()
    except ATError:
        pass

def phone_status():
    data = []
    status = phone.get_status()
    callerid = {}
    if status["state"] != "idle":
        callerid = phone.get_caller_id()
    for key, value in status.iteritems():
        if value:
            data.append("{}: {}".format(key, value))
    for key, value in callerid.iteritems():
        data.append("{}: {}".format(key, value))
    return data

def call(number):
    Printer("Calling {}".format(number), i, o, 0)
    try:
        phone.call(number)
    except ATError as e:
        Printer(ffs("Calling fail! "+repr(e), o.cols), i, o, 0)
    print("Function stopped executing")
 
def call_view():
    keymap = {"KEY_ANSWER":[call, "value"]}
    NumberKeypadInputLayer(i, o, "Call number", keymap, name="Phone call layer").activate()

def status_refresher():
    Refresher(phone_status, i, o).activate()

def check_modem_connection(bg=False):
    global modem, phone, connecting
    if not bg: Printer(ffs("Connecting to modem", o.cols), i, o, 0)
    if connecting.isSet(): return False
    if phone.modem is not None: return True
    connecting.set()
    try:
        modem = Modem()
        modem.init_modem()
        modem.start_monitoring()
        phone.attach_modem(modem)
        connecting.clear()
        return True
    except ValueError as e:
        print(repr(e)) 
        #Rollback
        if not bg: Printer(ffs("Modem connection failed", o.cols), i, o)
        modem.stop_monitoring()
        modem.deinit_modem()
        modem = None
        connecting.clear()
        return False

def init_app(input, output):
    global i, o, phone
    i = input; o = output 
    i.set_maskable_callback("KEY_ANSWER", answer)
    i.set_nonmaskable_callback("KEY_HANGUP", hangup)
    phone = Phone()
    try:
        #This not good enough - either make the systemctl library system-wide or add more checks
        os_call(["systemctl", "stop", "serial-getty@ttyAMA0.service"])
    except Exception as e:
        print(repr(e))
        #import pdb;pdb.set_trace()
    Thread(target=check_modem_connection, args=[True]).start()

def callback():
    if not check_modem_connection():
        Printer(ffs("Modem connection failed. Try again in 10 seconds.", o.cols), i, o)
        return
    contents = [["Status", status_refresher],
                ["Call", call_view]]
    Menu(contents, i, o).activate()
