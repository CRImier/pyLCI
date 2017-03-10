menu_name = "Refresher app" 

from ui import Refresher

counter = 0
keys_called = []

def process_key(key, *args):
    global counter, keys_called
    if len(keys_called) >= o.rows:
        keys_called = keys_called[1:]
    keys_called.append([counter, key])
    counter += 1
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
    callback = refresher.activate

