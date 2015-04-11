import socket
net_port = 6000 
import pickle
import select
import string
import sys

sock = None

def divide_data(message) :
    data = [message[:16], message[:32][16:]]
    serialized_data = pickle.dumps(data)
    return serialized_data
 
#main function
def init():     
    global sock
    host = 'localhost'
    port = 6000
     
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
     
    # connect to remote host
    try :
        sock.connect((host, port))
    except :
        print 'Unable to connect'
        sys.exit()
     
    print 'Connected to remote host. Start sending messages'
     

init()
if __name__ == "__main__":
    while True:
        msg = raw_input(":")
        sock.send(divide_data(msg))

