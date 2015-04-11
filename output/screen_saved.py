import select                                                                   
import threading                                                                
                                                                                
ser_port = "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A9CJVD59-if00-port0"     
                                                                                
class Screen():                                                                 
    type = "char"                                                               
    rows = 2                                                                    
    columns = 16                                                                
    def __init__(self):                                                         
        self.ser = Serial(ser_port, 115200)                                     
        ser.write("Loading...")                                                 
    def display_string(self, first_row, second_row):                            
        first_row = first_row[:self.columns].ljust(self.columns)                
        second_row = second_row[:self.columns].ljust(self.columns)              
        ser.write(first_row+second_row)                                         
                                                                                
class ScreenDriver():                                                           
    mode = None                                                                 
    def __init__(self, socket=True):                                            
        if socket:                                                              
            self.server = Server()                                              
        self.screen = Screen()                                                  
                                                                                
    def display_data (self, message):                                           
        print message                                                           
        print pickle.loads(message)                                             
        self.screen.display_string(*pickle.loads(message))                      
                                                                                
class Server()                                                                  
    self.socket_enabled = False                                                 
    def __init__(self, socket=True):                                            
        if socket:                                                              
            self.socket_enabled = True                                          
            self.init_socket()                                                  
            self.start_server()                                                 
        self.screen = Screen()                                                  