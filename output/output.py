from time import sleep
import socket
import pickle
import select
import threading
from helpers.config_parse import read_config
import importlib

#Currently only 16x2 char displays are fully supported and tested, as I simply don't have access to a bigger one yet -_-
#TODO: make a protocol for client-server messaging
#TODO: switch modes from direct-only to socket-only

net_port = 6000

def listen(screen):     
    """A blocking function that receives data over sockets and sends that directly to the screen"""
    CONNECTION_LIST = [] # List to keep track of socket descriptors
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
     
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("127.0.0.1", net_port))
    server_socket.listen(10)
    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)
    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
        for sock in read_sockets:
            #New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
                print "Client (%s, %s) connected" % addr
                 
            #Some incoming message from a client
            else:
                # Data recieved from client, process it
                try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        screen.display_string(*pickle.loads(data))               
                except:
                    raise
                    """#Client disconnected
                    print "Client (%s, %s) is offline" % addr
                    sock.close()
                    CONNECTION_LIST.remove(sock)
                    continue"""
    server_socket.close()


if "__name__" != "__main__":
    config = read_config()
    driver_name = config["output"][0]["driver"]
    driver_module = importlib.import_module("output.drivers."+driver_name)
    try:
        driver_args = config["output"][0]["driver_args"]
    except KeyError:
        driver_args = []
    try:
        driver_kwargs = config["output"][0]["driver_kwargs"]
    except KeyError:
        driver_kwargs = {}
    screen = driver_module.Screen(*driver_args, **driver_kwargs)
    listener_thread = threading.Thread(target=listen, args=(screen,))
    listener_thread.daemon = True
    listener_thread.start()
