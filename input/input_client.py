from evdev import InputDevice, list_devices, categorize, ecodes
import threading
import socket
import pickle
import select
net_port = 6001 

debug = True

class NetKeyListener():
    """A class which listens for input device events sent by Listener over sockets and calls according callbacks if set"""
    enabled = False
    listening = False
    keymap = {}
    stop_flag = True

    def __init__(self):     
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

    def get_keys(self, device):
        """Gets all the available keys of input device"""

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
        """Sends a message to server"""
        serialized_data = pickle.dumps(data, 2)
        self.socket.send(serialized_data)

    def get_messages(self):
        """Gets incoming messages from server, returning a list of messages received at the moment"""
        data = self.socket.recv(4096)
        #Imagine that we have received 2 or more messages in a row, basically, two concatenated pickled dicts. 
        #In that case, 'pickle.loads' will return only the first. So, here's a workaround to avoid losing messages.
        messages = [] 
        while data: 
            try:
                message = pickle.loads(data)
            except:
                break #Will have to make further tests to see if that's possible. I can think of network connection issues or receiving of data which wasn't fully sent
            else:
                offset = len(pickle.dumps(message, 2))
                data = data[offset:]
                messages += message
        #My wish is to get anonymous e-mails if len(messages) > 1. I wonder if that actually will happen ;-) Will see myself, though.
        return messages

    def process_events_in_loop(self):
        """A blocking function that gets messages from server and processes them"""
        self.listening = True
        try:
            while not self.stop_flag:
                read_sockets,write_sockets,error_sockets = select.select(self.socket,[],[], 0.01)
                if read_sockets:
                    messages = get_messages()
                    for message in messages:
                        if message.keys[0] == 'callback':
                            key = message['callback'][0]
                            value = message['callback'][1]
                            if value == 0:
                                if key in self.keymap:
                                    if debug: print "Received event that has a callback set, calling it"
                                    self.keymap[key][0]()
        except KeyError as e:
            self.force_disable()
        finally:
            self.listening = False

    def listen(self):
        """A non-blocking function that starts 'process_events_in_loop' thread"""
        if debug: print "started listening"
        self.stop_flag = False
        self.listener_thread = threading.Thread(target = self.process_events_in_loop) 
        self.listener_thread.daemon = True
        self.listener_thread.start()
        return True

    def stop_listen(self):
        """A function that stops 'process_events_in_loop' thread"""
        self.stop_flag = True
        return True


def get_input_devices():
    return [InputDevice(fn) for fn in list_devices()]

if __name__ == "__main__":
    listener = NetKeyListener()
    
