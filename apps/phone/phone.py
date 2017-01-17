from threading import Event, Thread
from Queue import Queue, Empty
from serial import Serial
from time import sleep
import logging
import string
import shlex

def has_nonascii(s):
    ascii_chars = string.ascii_letters+string.digits+"!@#$%^&*()_+\|{}[]-_=+'\",.<>?:; "
    return any([char for char in ascii_chars if char not in ascii_chars])

def is_csv(s):
    return "," in s

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
    clcc_header = "+CLCC:"

    def __init__(self, serial_path="/dev/ttyAMA0", timeout=0.2, monitor=True):
        self.serial_path = serial_path
        self.read_timeout = timeout
        self.executing_command = Event()
        self.should_monitor = Event()
        self.unexpected_queue = Queue()
        if monitor: self.start_monitoring()

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

    def process_clcc(self, clcc_line):
        if clcc_line.startswith(self.clcc_header):
            clcc_line = clcc_line[len(self.clcc_header):]
        clcc_line = clcc_line.strip()
        elements = shlex.split(clcc_line, ',')
        if len(elements) < 8:
            print("Unrecognized number of CLCC elements!")
            print(repr(elements))
            return
        elif len(elements) > 8:
            print("Too much CLCC elements!")
            elements = elements[:8]
        
        

    def call(self, number):
        return self.at_command("ATD{};".format(number))

    def hangup(self):
        return self.at_command("ATH", noresponse=True)

    def answer(self):
        return self.at_command("ATA")

    #Callbacks - to be overridden

    def on_active_call(self):
        print("Call is active - is it ever?")

    def on_ring(self):
        print("Ring ring ring bananaphone!")

    def on_dialing(self):
        print("Hope somebody answers...")

    def on_busy(self):
        print("Can't you see it's busy")

    def on_hangup(self):
        print("The person you were talking to got seriously bored")

    def on_noanswer(self):
        print("Somebody's tired of your shit")

    def on_incoming_message(self, cmti_line):
        print("You've got mail! Line: {}".format(cmti_line[len("+CMTI:"):]).strip())

    clcc_mapping = [ #Outgoing
    {
    "0":on_active_call,
    "1":on_held,
    "2":on_active_call,
    "3":on_active_call,
    "4":on_active_call,
    "5":on_active_call,
    "6":on_hangup}
    ],             [ #Incoming
    {
    "0":on_active_call,
    "1":on_held,
    "2":on_active_call,
    "3":on_active_call,
    "4":on_active_call,
    "5":on_active_call,
    "6":on_hangup}
    ],

    def on_clcc(self, clcc_line):
        #CLCC is operator-dependent, from what I understand.
        for i in range(4):
            if not has_nonascii(clcc_line) or not is_csv(clcc_line): 
                break
            print("Garbled caller ID line! Try {}, line: {}".format(i, clcc_line))
            sleep(1)
            clcc_response = self.at_command("AT+CLCC", nook=True)
            print(repr(lines))
            for line in lines:
                if line.startswith(self.clcc_header):
                    clcc_line = line
                else:
                    self.queue_unexpected_data(line)
        if has_nonascii(clcc_line) or not is_csv(clcc_line):
            print("Still garbled CLCC line!"); return
        print("Caller ID OK, line: {}".format(repr(clcc_line[len(self.clcc_header):])).strip())
        #self.process_clcc(clcc_line)

    #Low-level functions

    def check_input(self):
        #print("Checks input")
        input = self.port.read(self.read_buffer_size)
        if input:
            self.queue_unexpected_data(input)

    def at_command(self, command, noresponse=False, nook=False):
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
        if nook: return lines
        if self.ok_response not in lines: #expecting OK as one of the elements 
            raise ATError(expected=self.ok_response, received=lines)
        #We can have a sudden undervoltage warning, though
        #I'll assume the OK always goes last in the command
        #So we can pass anything after OK to the unexpected line parser
        ok_response_index = lines.index(self.ok_response)
        if ok_response_index+1 < len(lines):
            self.queue_unexpected_data(lines[(ok_response_index+1):])
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

    def queue_unexpected_data(self, data):
        self.unexpected_queue.put(data) 

    def process_incoming_data(self, data):
        logging.debug("Incoming data: {}".format(repr(data)))
        if isinstance(data, str):
            data = data.split(self.linesep)            
        lines = filter(None, data)
        for line in lines:
            #Now onto the callbacks
            if line == "RING":
                self.on_ring(); return
            if line == "BUSY":
                self.on_busy(); return
            if line == "HANGUP":
                self.on_hangup(); return
            if line == "NO ANSWER":
                self.on_no_answer(); return
            if line in ["SMS Ready", "Call Ready"]:
                pass; return #Modem just reset
            if line.startswith("+CMTI:"):
                self.on_incoming_message(line); return
            if line.startswith("+CLCC:"):
                self.on_clcc(line); return
        self.parse_unexpected_message(lines)
        
    def parse_unexpected_message(self, data):
        #haaaax
        if self.linesep[::-1] in "".join(data):
            lines = "".join(data).split(self.linesep[::-1])
        logging.debug("Unexpected lines: {}".format(data))
        
    def monitor(self):
        while self.should_monitor.isSet():
            #print("Monitoring...")
            if not self.executing_command.isSet():
                #First, the serial port
                data = self.port.read(self.read_buffer_size)
                if data: 
                    print("Got data through serial!")
                    self.process_incoming_data(data)
                #Then, the queue of unexpected messages received from other commands
                try:
                    data = self.unexpected_queue.get_nowait()
                except Empty:
                    pass
                else:
                    print("Got data from queue!")
                    self.process_incoming_data(data)
            #print("Got to sleep")
            sleep(self.read_timeout)
            #print("Returned from sleep")
        print("Stopped monitoring!")

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
