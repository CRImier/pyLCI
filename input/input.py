from evdev import InputDevice, list_devices, categorize, ecodes
import threading
import time
import os
import importlib
import select
from config_parse import read_config
try:
    import cPickle as pickle
except ImportError:
    import pickle
import socket
debug = True

#TODO: add server-client communication for requesting listeners and getting listener info
#TODO: add a function getting all the keys of listener

def to_be_enabled(func):
    """Decorator for KeyListener class. Is used on functions which require enabled KeyListener to be executed. 
       Currently assumes there has been an error and tries to re-enable the listener."""
    def wrapper(self, *args, **kwargs):
        if not self.enabled:
            if not self.enable():
                return None #TODO: think what's appropriate and what are the times something like that might happen
        else:
            return func(self, *args, **kwargs)
    return wrapper

class KeyListener():
    """A class which listens for input device events and calls according callbacks if set"""
    socket_mode = False
    enabled = False
    listening = False
    keymap = {}
    stop_flag = False

    def __init__(self, path=None, name=None, keymap={}):
        """Init function for creating KeyListener object. Checks all the arguments and sets keymap if supplied."""
        if not name and not path: #No necessary arguments supplied
            raise TypeError("Expected at least path or name; got nothing. =(")
        if not path:
            path = get_path_by_name(name)
        if not name:
            name = get_name_by_path(path)
        if not name and not path: #Seems like nothing was found by get_input_devices
            raise IOError("Device not found")
        self.path = path
        self.name = name
        self.set_keymap(keymap)
        self.enable()

    def enable(self):
        """Enables listener - sets all the flags and creates devices. Does not start a listening or a listener thread."""
        #TODO: make it re-check path if name was used for the constructor
        #keep in mind that this will get called every time if there's something wrong
        #and input device file nodes aren't strictly mapped to their names
        #__init__ function remake is needed for this
        if debug: print "enabling listener"
        try:
            self.device = InputDevice(self.path)
        except OSError:
            raise
        try:
            self.device.grab() #Catch exception if device is already grabbed
        except IOError:
            pass
        self.enabled = True
        return True

    @to_be_enabled
    def force_disable(self):
        """Disables listener, is useful when device is unplugged and errors may occur when doing it the right way
           Does not unset flags - assumes that they're already unset."""
        if debug: print "forcefully disabling listener"
        self.stop_listen()
        #Exception possible at this stage if device does not exist anymore
        #Of course, nothing can be done about this =)
        try:
            self.device.ungrab() 
        except IOError:
            pass #Maybe log that device disappeared?
        self.enabled = False

    @to_be_enabled
    def disable(self):
        """Disables listener - makes it stop listening and ungrabs the device"""
        if debug: print "disabling listener"
        self.stop_listen()
        while self.listening:
            if debug: print "still listening"
            time.sleep(0.01)
        self.device.ungrab()
        self.enabled = False

    def set_callback(self, key_name, callback):
        """Sets a single callback of the listener"""
        self.keymap[key_name] = callback

    def remove_callback(self, key_name):
        """Sets a single callback of the listener"""
        self.keymap.remove(key_name)

    def set_keymap(self, keymap):
        """Sets all the callbacks supplied, removing previously set"""
        self.keymap = keymap

    def replace_keymap_entries(self, keymap):
        """Sets all the callbacks supplied, not removing previously set"""
        for key in keymap.keys:
            set_callback(key, keymap[key])

    def clear_keymap(self):
        """Removes all the callbacks set"""
        self.keymap.clear()

    @to_be_enabled
    def process_message(self, message):
        """Processes messages sent by clients over the sockets.
           Currently no implemented as no message specification is yet designed"""
        pass

    @to_be_enabled
    def socket_event_loop(self):
        """Blocking event loop which both listens for input events, sending them over the sockets, 
           and listens for incoming messages over the sockets. Doesn't react to callbacks in the keymap."""
        net_port = 6001
        CONNECTION_LIST = [] # List to keep track of socket descriptors
        RECV_BUFFER = 4096 
        fileno = self.device.fileno()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("0.0.0.0", net_port))
        server_socket.listen(10)
        # Add server socket to the list of readable connections
        CONNECTION_LIST.append(server_socket)
        CONNECTION_LIST.append(fileno)
        self.listening = True
        try:
            while not self.stop_flag:
                read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[], 0.01)
                if read_sockets:
                    # Handle the case in which there is a new connection recieved through server_socket
                    for sock in read_sockets:
                        if sock == server_socket:
                            #New connection
                            sockfd, addr = server_socket.accept()
                            CONNECTION_LIST.append(sockfd)
                            print "Client (%s, %s) connected" % addr
                        elif sock == fileno:
                            event = self.device.read_one()
                            while event:
                                if event.type == ecodes.EV_KEY:
                                    key = ecodes.keys[event.code]
                                    value = event.value
                                    if value == 0:
                                        message = {"callback":[key, value]}
                                        pickle.dumps(message)
                                        if debug: print "processing an event: "+str(message)
                                        self.send_over_socket(pickle.dumps(message))
                                event = self.device.read_one()
                        else:  #Some incoming message from a client
                            # Data recieved from client, process it
                            try:
                                #In Windows, sometimes when a TCP program closes abruptly,
                                # a "Connection reset by peer" exception will be thrown
                                pickled_data = sock.recv(RECV_BUFFER)
                                if pickled_data:
                                    data = pickle.loads(pickled_data)
                                    self.process_message(data)   
                            except: #Client has disconnected
                                print "Client (%s, %s) is offline" % addr
                                sock.close()
                                CONNECTION_LIST.remove(sock)
                                continue
        except KeyError as e:
            self.force_disable()
        finally: 
            server_socket.close()
            self.listening = False

    @to_be_enabled
    def direct_event_loop(self):
        """Blocking event loop which just calls supplied callbacks in the keymap. Doesn't work with sockets."""
        #TODO: describe callback interpretation ways
        self.listening = True
        try:
            for event in self.device.read_loop():
                if self.stop_flag:
                    break
                if event.type == ecodes.EV_KEY:
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
        except IOError as e: 
            if e.errno == 11:
                #Okay, this error sometimes appears out of blue when I press buttons on a keyboard. Moreover, it's uncaught but due to some logic I don't understand yet the whole thing keeps running. I need to research it.
                print("That error again. Need to learn to ignore it somehow.")
        finally:
            self.listening = False

    @to_be_enabled
    def listen_direct(self):
        """Start direct mode event loop in a thread. Nonblocking."""
        self.socket_mode = False
        if debug: print "started listening"
        self.stop_flag = False
        self.listener_thread = threading.Thread(target = self.direct_event_loop) 
        self.listener_thread.daemon = True
        self.listener_thread.start()
        return True

    @to_be_enabled
    def listen_socket(self):
        """Start socket mode event loop in a thread. Nonblocking."""
        self.socket_mode = True
        if debug: print "started listening"
        self.stop_flag = False
        self.listener_thread = threading.Thread(target = self.socket_event_loop) 
        self.listener_thread.daemon = True
        self.listener_thread.start()
        return True

    @to_be_enabled
    def stop_listen(self):
        self.stop_flag = True
        return True

def get_input_devices():
    """Returns list of all the available InputDevices"""
    return [InputDevice(fn) for fn in list_devices()]

def get_path_by_name(name):
    """Gets HID device path by name, returns None if not found."""
    path = None
    for dev in get_input_devices():
        if dev.name == name:
            path = dev.fn
    return path

def get_name_by_path(path):
    """Gets HID device path by name, returns None if not found."""
    name = None
    for dev in get_input_devices():
        if dev.fn == path:
            name = dev.name
    return name

if "__name__" != "__main__":
    config = read_config()
    try:
        driver_name = config["input"][0]["driver"]
    except:
        driver_name = None
    if driver_name:
        driver_module = importlib.import_module("input.drivers."+driver_name)
        try:
            driver_args = config["input"][0]["driver_args"]
        except KeyError:
            driver_args = []
        try:
            driver_kwargs = config["input"][0]["driver_kwargs"]
        except KeyError:
            driver_kwargs = {}
        driver = driver_module.InputDevice(*driver_args, **driver_kwargs)
        driver.activate()
    try:
        device_name = config["input"][0]["device_name"]
    except:
        device_name = driver.name
    while get_path_by_name(device_name) == None:
          print("Device {} not yet available, waiting...".format(device_name))
          print("Available input devices: {}".format([device.name for device in get_input_devices()]))
          time.sleep(1)
    listener = KeyListener(name=device_name)

