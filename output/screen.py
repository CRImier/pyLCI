from serial import Serial
from time import sleep
import socket 
import pickle
import select
import threading

net_port = 6000
ser_port = "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A9CJVD59-if00-port0"
 
class Screen():
    type = "char"
    rows = 2
    columns = 16
    def __init__(self, serial):
        self.serial = serial
        serial.write("Loading...")
    def display_string(self, first_row, second_row):
        first_row = first_row[:self.columns].ljust(self.columns)
        second_row = second_row[:self.columns].ljust(self.columns)
        self.serial.write(first_row+second_row)

class ScreenDriver():
    mode = None
    def __init__(self, screen, socket=True):
#        if socket:
#            self.server = Server()
        self.screen = screen

    def display_data (self, message):
        print message
        print pickle.loads(message)
        self.screen.display_string(*pickle.loads(message))

"""
class Server():
    socket_enabled = False
    def __init__(self, socket=True):
        if socket:
            self.socket_enabled = True
            self.init_socket()
            self.start_server()
        self.screen = Screen()
"""
 
def listen(screen_driver):     
    # List to keep track of socket descriptors
    CONNECTION_LIST = []
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
                        screen_driver.display_data(data)               
                except:
                    #Client disconnected
                    print "Client (%s, %s) is offline" % addr
                    sock.close()
                    CONNECTION_LIST.remove(sock)
                    continue
     
    server_socket.close()




serial = Serial(ser_port, 115200)
screen = Screen(serial)
screendriver = ScreenDriver(screen)
listener_thread = threading.Thread(target=listen, args=(screendriver,))
listener_thread.daemon = True
listener_thread.start()
send_string = screen.display_string


