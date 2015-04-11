from evdev import InputDevice, list_devices, categorize, ecodes
import threading
import time
import os
import pickle
import socket
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
    socket_mode = False
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
    def socket_event_loop(self):
        net_port = 6000
        CONNECTION_LIST = [] # List to keep track of socket descriptors
        RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("0.0.0.0", net_port))
        server_socket.listen(10)
        # Add server socket to the list of readable connections
        CONNECTION_LIST.append(server_socket)
        self.listening = True
        try:
            for event in self.device.read_loop():
                if self.stop_flag:
                    return True
                if event.type == ecodes.EV_KEY:
                    key = ecodes.keys[event.code]
                    value = event.value
                    if value == 0:
                        message = {"callback":[key, value]}
                        pickle.dumps(message)
                        if debug: print "processing an event: "+str(message)
                        self.send_over_socket(message)
                read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[], 0.01)
                if read_sockets:
                    # Handle the case in which there is a new connection recieved through server_socket
                    for sock in read_sockets:
                        if sock == server_socket:
                            #New connection
                            sockfd, addr = server_socket.accept()
                            CONNECTION_LIST.append(sockfd)
                            print "Client (%s, %s) connected" % addr
                        else:  #Some incoming message from a client
                            # Data recieved from client, process it
                            try:
                                #In Windows, sometimes when a TCP program closes abruptly,
                                # a "Connection reset by peer" exception will be thrown
                                data = sock.recv(RECV_BUFFER)
                                if data:
                                    print data              
                            except:
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
                            if len(self.keymap[key]) > 1: #callback has to be supplied arguments if they are enclosed in the list
                                self.keymap[key][0](*self.keymap[key][1])
                            else: 
                                self.keymap[key][0]()
                        else:
                            print ""
        except KeyError as e:
            self.force_disable()
        finally:
            self.listening = False


    @to_be_enabled
    def send_over_socket(self, message):
        pass


    @to_be_enabled
    def listen_direct(self):
        self.socket_mode = False
        if debug: print "started listening"
        self.stop_flag = False
        self.listener_thread = threading.Thread(target = self.direct_event_loop) 
        self.listener_thread.daemon = True
        self.listener_thread.start()
        return True

    @to_be_enabled
    def listen_socket(self):
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
    return [InputDevice(fn) for fn in list_devices()]



