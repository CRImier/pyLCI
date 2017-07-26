menu_name = "Refresher app" 

from ui import Refresher, Printer, format_for_screen as ffs

counter = 0
keys_called = []

def process_key(key, *args):
    global counter, keys_called
    if len(keys_called) >= o.rows:
        keys_called = keys_called[1:]
    keys_called.append([counter, key])
    counter += 1
    last_three_keys = [k for c, k in keys_called][-3:]
    keys_are_left = [k=="KEY_LEFT" for k in last_three_keys]
    if len(last_three_keys) >= 3 and all(keys_are_left):
        refresher.deactivate()
    else:
        refresher.refresh() #Makes changes appear faster

def get_keys():
    return ["{}:{}".format(num, key) for num, key in keys_called]

refresher = None
callback = None
i = None #Input device
o = None #Output device

def init_app(input, output):
    global refresher, callback, i, o
    i = input; o = output 
    i.set_streaming(process_key)
    refresher = Refresher(get_keys, i, o, 1, name="Key monitor")
    refresher.keymap.pop("KEY_LEFT") #Removing deactivate callback to show KEY_LEFT
    Printer(ffs("To exit this app, press LEFT 3 times", o.cols), i, o)
    callback = refresher.activate

