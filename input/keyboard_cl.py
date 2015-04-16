from evdev import InputDevice, list_devices, categorize, ecodes
import threading
import socket
import pickle
import select
net_port = 6001 

debug = True

class NetKeyListener():
    enabled = False
    listening = False
    keymap = {}
    stop_flag = True

    def __init__(self):     
        #TODO: get some kind of display parameters to correctly send data
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect(('127.0.0.1', net_port))
        self.socket = s

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

    def send_message(self, message):
        serialized_data = pickle.dumps(data)
        self.socket.send(serialized_data)

    def get_message(self):
        data = self.socket.recv(4096)
        if data: ####OMG MULTIPLE MESSAGES CONCATENATED ABORT ABORT

    def process_events_in_loop(self):
        self.listening = True
        try:
            while not self.stop_flag:
                read_sockets,write_sockets,error_sockets = select.select(self.socket,[],[], 0.01)
                message = 


            for event in self.device.read_loop():
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

    def listen(self):
        if debug: print "started listening"
        self.stop_flag = False
        self.listener_thread = threading.Thread(target = self.process_events_in_loop) 
        self.listener_thread.daemon = True
        self.listener_thread.start()
        return True

    def stop_listen(self):
        self.stop_flag = True
        return True


def get_input_devices():
    return [InputDevice(fn) for fn in list_devices()]


if __name__ == "__main__":
    listener = NetListener(#####ARGUMENTS)
    """while True:
        message = raw_input(":")
        screen.send_string(message)"""

















    """A class which listens for input device events and calls according callbacks if set"""

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
            while not stop_flag:
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


