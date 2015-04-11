from serial import Serial
from time import sleep
import socket 
import pickle
import select

net_port = 6000
ser_port = "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A9CJVD59-if00-port0"
ser = Serial(ser_port, 115200)
 
def display_data (message):
    print message
    print pickle.loads(message)
    display_string(*pickle.loads(message))
 
def listen():     
    # List to keep track of socket descriptors
    CONNECTION_LIST = []
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
     
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this has no effect, why ?
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", net_port))
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
                        display_data(data)               
                except:
                    print "Client (%s, %s) is offline" % addr
                    sock.close()
                    CONNECTION_LIST.remove(sock)
                    continue
     
    server_socket.close()



def display_string(first_row, second_row):
    first_row = first_row[:16].ljust(16)
    second_row = second_row[:16].ljust(16)
    ser.write(first_row+second_row)

send_string = display_string

#listen()
