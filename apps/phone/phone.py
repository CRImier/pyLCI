menu_name = "Phone" 

from threading import Event, Thread
from time import sleep

from serial import Serial

#from ui import Refresher, Menu
#from helpers import read_config, write_config

i = None 
o = None

serial_device = "/dev/ttyAMA0"
#serial_device = "/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0"

class ATError(Exception):
    def __init__(self, expected=None, received=None):
        self.received = received
        self.expected = expected
        message = "Expected {}, got {}".format(expected, repr(received))
        Exception.__init__(self, message)
        self.received = received

class Modem():
    read_buffer_size = 1000
    read_timeout = 0.2

    manufacturer = None
    model = None

    linesep = '\r\n'
    ok_response = 'OK'
    reset_marker = "reset ..."
    power_on_reset_timeout = 10

    def __init__(self, timeout = 0.2):
        self.read_timeout = timeout
        self.executing_command = Event()
        self.should_monitor = Event()

    def init_modem(self):
        self.port = Serial(serial_device, 115200, timeout=self.read_timeout)
        self.at()
        self.enable_verbosity()
        print("Battery voltage is: {}".format(self.get_voltage()))
        self.manufacturer = self.at_command("AT+CGMI")
        self.model = self.at_command("AT+CGMM")

    def enable_verbosity(self):
        return self.at_command('AT+CMEE=1')

    def at(self):
        response = self.at_command('AT')
        if response is True: return
        raise ATError(expected=self.ok_response, received=response)

    def get_voltage(self):
        answer = self.at_command('AT+CBC')
        if not answer.startswith('+CBC'): return 0.0
        voltage_str = answer.split(':')[1].split(',')[2]
        voltage = round(int(voltage_str)/1000.0, 2)
        return voltage

    def call(self, number):
        return self.at_command("ATD{};".format(number))

    def hangup(self):
        return self.at_command("ATH", noresponse=True)

    def answer(self):
        return self.at_command("ATA")

    #Callbacks - to be overridden

    def signal_ring(self):
        print("Ring ring ring bananaphone!")

    def signal_incoming_message(self):
        print("You've got mail!")

    #Low-level functions

    def check_input(self):
        input = self.port.read(self.read_buffer_size)
        if input:
            self.process_incoming_data(input)

    def at_command(self, command, noresponse=False):
        self.executing_command.set()
        self.check_input()
        self.port.write(command+self.linesep)
        echo = self.port.read(len(command)) #checking for command echo
        if echo != command:
            raise ATError(received=echo, expected=command)
        #print(repr(self.port.read(len(self.linesep)+1))) 
        self.port.read(len(self.linesep)+1) #shifting through the line separator - that +1 seems to be necessary when we're reading right after the echo
        answer = self.port.read(self.read_buffer_size)
        self.executing_command.clear()
        lines = filter(None, answer.split(self.linesep))
        #print(lines)
        if not lines: return True if noresponse else False             
        if len(lines) == 1: #Single-line response
            if lines[0] == self.ok_response: 
                return True
            else:
                return lines[0]
        else:
            if lines[-1] != self.ok_response: #expecting OK as the last element
                raise ATError(expected=self.ok_response, received=lines)
            lines = lines[:-1]
            if len(lines) == 1:
                return lines[0]
            else:
                return lines

    def process_incoming_data(self, data):
        lines = filter(None, data.split(self.linesep))
        if len(lines) == 1:
            line = lines[0]
            if line == "RING":
                self.signal_ring(); return
            if line == "SMS Ready":
                pass; return #Modem just reset
            if line == "Call Ready":
                pass; return #Modem just reset
            elif line.startswith("+CMTI:"):
                self.signal_incoming_message(); return
        self.parse_unexpected_message(lines)
        
    def parse_unexpected_message(self, data):
        if self.linesep[::-1] in "".join(data):
            #haaaax
            lines = "".join(data).split(self.linesep[::-1])
            if "reset ..." in " ".join(lines):
                print("Modem reset")
                for i in range(self.power_on_reset_timeout):
                    try:
                        self.at()
                    except ATError:
                        sleep(1)
                    else:
                        break
                sleep(3)
                self.init_modem()
                return
            else:
                print("Unexpected lines: {}".format(lines)); return
        print("Unexpected lines: {}".format(data))
        
    def monitor(self):
        while self.should_monitor.isSet():
            if not self.executing_command.isSet():
                data = self.port.read(self.read_buffer_size)
                if data: self.process_incoming_data(data)
                sleep(self.read_timeout)
            else:
                sleep(self.read_timeout*2)

    def start_monitoring(self):
        self.should_monitor.set()
        self.thread = Thread(target=self.monitor)
        self.thread.daemon=True
        self.thread.start()

    def stop_monitoring(self):
        self.should_monitor.clear()

if __name__ == "__main__":
    modem = Modem(timeout = 0.5)
    modem.init_modem()
    modem.start_monitoring()
    while True:
        try:
            print(modem.get_voltage())
        except ATError:
            print ATError.received
        except Eception as e:
            print(repr(e))
