import socket
import pickle
net_port = 6000 

#TODO: remake for 4-line display support... As soon as I get one =(

class NetScreen():
    """A simple screen-over-socket class for use by external programs"""
    def __init__(self):     
        #TODO: get some kind of display parameters to correctly send data
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect(('127.0.0.1', net_port))
        self.socket = s
    def send_string(self, message):
        """Sends a string on the screen, dividing it as necessary"""
        self.send_data([message[:16], message[:32][16:]])
    def send_data(self, data):
        """Sends 2 strings to the screen, showing each one on a separate line"""
        serialized_data = pickle.dumps(data)
        self.socket.send(serialized_data)

if __name__ == "__main__":
    screen = NetScreen()
    while True:
        message = raw_input(":")
        screen.send_string(message)

