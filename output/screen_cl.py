import socket
import pickle
net_port = 6000 

class NetScreen():
    def __init__(self):     
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(('127.0.0.1', net_port))
        self.sock = sock
    def send_string(self, message):
        self.send_data([message[:16], message[:32][16:]])
    def send_data(self, data):
        serialized_data = pickle.dumps(data)
        self.sock.send(serialized_data)

if __name__ == "__main__":
    screen = NetScreen()
    while True:
        message = raw_input(":")
        screen.send_string(message)

