from threading import Event, Thread
from Queue import Queue, Empty
from serial import Serial
from time import sleep

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
    unexpected_queue = None

    manufacturer = None
    model = None

    linesep = '\r\n'
    ok_response = 'OK'
    error_response = 'ERROR'

    def __init__(self, serial_path="/dev/ttyAMA0", timeout=0.2):
        self.serial_path = serial_path
        self.read_timeout = timeout
        self.executing_command = Event()
        self.should_monitor = Event()
        self.unexpected_queue = Queue()

    def init_modem(self):
        self.port = Serial(self.serial_path, 115200, timeout=self.read_timeout)
        self.at()
        self.enable_verbosity()
        print("Battery voltage is: {}".format(self.get_voltage()))
        self.manufacturer = self.at_command("AT+CGMI")
        self.model = self.at_command("AT+CGMM")
        self.at_command("AT+CLIP=1")
        self.save_settings()

    def save_settings(self):
        self.at_command("AT&W")

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
            self.process_unexpected_data(input)

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
        if not lines and noresponse: return True #one of commands that doesn't need a response
        if self.ok_response not in lines: #expecting OK as one of the elements 
            raise ATError(expected=self.ok_response, received=lines)
        #We can have a sudden undervoltage warning, though
        #I'll assume the OK always goes last in the command
        #So we can pass anything after OK to the unexpected line parser
        ok_response_index = lines.index(self.ok_response)
        if ok_response_index+1 < len(lines):
            self.process_unexpected_data(lines[(ok_response_index+1):])
            lines = lines[:(ok_response_index+1)]
        if len(lines) == 1: #Single-line response
            if lines[0] == self.ok_response: 
                return True
            else:
                return lines[0]
        else: 
            lines = lines[:-1]
            if len(lines) == 1:
                return lines[0]
            else:
                return lines

    #Functions for background monitoring of any unexpected input

    def process_unexpected_data(self, data):
        self.unexpected_queue.put(data) 

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
        self.process_unexpected_message(lines)
        
    def parse_unexpected_message(self, data):
        #haaaax
        if self.linesep[::-1] in "".join(data):
            lines = "".join(data).split(self.linesep[::-1])
            print("Unexpected lines: {}".format(lines)); return
        print("Unexpected lines: {}".format(data))
        
    def monitor(self):
        while self.should_monitor.isSet():
            if not self.executing_command.isSet():
                data = self.port.read(self.read_buffer_size)
                if data: 
                    self.process_incoming_data(data)
                try:
                    data = self.unexpected_queue.get()
                except Empty:
                    pass
                else:
                    self.process_incoming_data(data)
            sleep(self.read_timeout)

    def start_monitoring(self):
        self.should_monitor.set()
        self.thread = Thread(target=self.monitor)
        self.thread.daemon=True
        self.thread.start()

    def stop_monitoring(self):
        self.should_monitor.clear()


if __name__ == "__main__":
    modem = Modem(timeout = 0.5)
    modem.start_monitoring()
    modem.init_modem()
