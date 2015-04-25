from evdev import InputDevice, list_devices, categorize, ecodes
import threading
import time
import os
#import pickle

debug = True

def to_be_enabled(func):
    def wrapper(self, *args, **kwargs):
        if not self.enabled:
            if not self.enable():
                return False
        else:
            return func(self, *args, **kwargs)
    return wrapper

class KeyListener():
    enabled = False
    listening = False
    keymap = {}
    stop_flag = False

    def __init__(self, path=None, name=None, keymap={}):
        self.path = path
        self.name = name
        self.set_keymap(keymap)
        self.enable()

    def get_path(self): 
        #Problem. If device was selected by path, there will be an exception.
        #TODO: make this exception be something more human-understandable
        if self.path:
            return True
        for dev in get_input_devices():
            if dev.name == self.name:
                self.path = dev.fn
        if not self.path:
            return False
        else:
            return True

    def enable(self):
        #TODO: make it re-check path if name was used for the constructor
        #keep in mind that this will get called every time if there's something wrong
        #and input device file nodes aren't strictly mapped to their names
        #__init__ function remake is needed for this
        if debug: print "enabling listener"
        if not self.get_path():
            return False
        self.device = InputDevice(self.path)
        try:
            self.device.grab() #Catch exception if device is already grabbed
        except IOError:
            pass
        self.enabled = True
        return True

    @to_be_enabled
    def force_disable(self):
        if debug: print "forcefully disabling listener"
        self.stop_listen()
        #Exception possible at this stage if device does not exist anymore
        #Of course, nothing can be done about this =)
        try:
            self.device.ungrab() 
        except IOError:
            pass
        self.enabled = False

    @to_be_enabled
    def disable(self):
        if debug: print "disabling listener"
        self.stop_listen()
        while self.listening:
            if debug: print "still listening"
            time.sleep(0.01)
        self.device.ungrab()
        self.enabled = False

    def set_callback(self, key_name, callback):
        self.keymap[key_name] = callback

    def set_keymap(self, keymap):
        self.keymap = keymap

    @to_be_enabled
    def process_events_in_loop(self):
        self.listening = True
        try:
            for event in self.device.read_loop():
                if self.stop_flag:
                    break
                if event.type == ecodes.EV_KEY:
                    #print pickle.dumps([ecodes.keys[event.code], event.value])
                    key = ecodes.keys[event.code]
                    value = event.value
                    if value == 0:
                        if debug: print "processing an event: ",
                        if key in self.keymap:
                             if debug: print "event has callback, calling it"
                             self.keymap[key]()
                        else:
                             print ""
        except KeyError as e:
            self.force_disable()
        finally:
            self.listening = False

    @to_be_enabled
    def listen(self):
        if debug: print "started listening"
        self.stop_flag = False
        self.listener_thread = threading.Thread(target = self.process_events_in_loop) 
        self.listener_thread.daemon = True
        self.listener_thread.start()
        return True

    @to_be_enabled
    def stop_listen(self):
        self.stop_flag = True
        return True

def get_input_devices():
    return [InputDevice(fn) for fn in list_devices()]



