import smbus
from time import sleep
import threading

class InputDevice():
    mapping = [
    "KEY_DOWN",
    "KEY_UP",
    "KEY_KPENTER",
    "KEY_LEFT",
    "KEY_HOME",
    "KEY_END",
    "KEY_RIGHT",
    "KEY_DELETE"]
    stop_flag = False
    previous_data = 0

    def __init__(self, addr = 0x27, bus = 1, int_pin = None):
        self.bus_num = bus
        self.bus = smbus.SMBus(self.bus_num)
        self.addr = 0x3e
        self.int_pin = int_pin

    def start(self):
        self.stop_flag = False
        self.bus.write_byte(self.addr, 0xff)
        if self.int_pin is None:
            self.loop_polling()
        else:
            self.loop_interrupts()

    def loop_interrupts(self):
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
        GPIO.setup(self.int_pin, GPIO.IN)
        button_states = []
        try:
            while not self.stop_flag:
                while GPIO.input(self.int_pin) == False:
                    data = (~self.bus.read_byte(self.addr)&0xFF)
                    self.process_data(data)
                    self.previous_data = data
                sleep(0.1)
        except:
            raise
        finally:
            try:
                GPIO.cleanup()
            except:
                pass #Often fails like that when system terminates, doesn't seem to be harmful

    def loop_polling(self):
        button_states = []
        while not self.stop_flag:
            data = (~self.bus.read_byte(self.addr)&0xFF)
            if data != self.previous_data:
                self.process_data(data)
                self.previous_data = data
            sleep(0.1)

    def process_data(self, data):
        data_difference = data ^ self.previous_data
        changed_buttons = []
        for i in range(8):
            if data_difference & 1<<i:
                changed_buttons.append(i)
        for button_number in changed_buttons:
            if not data & 1<<button_number:
                self.send_key(self.mapping[button_number])

    def stop(self):
        self.stop_flag = True

    def send_key(self, key):
        """Is meant to be overridden by InputListener. Otherwise, is useful for debugging."""
        print(key)

    def activate(self):
        self.thread = threading.Thread(target=self.start)
        self.thread.daemon = False
        self.thread.start()


if __name__ == "__main__":
    id = InputDevice(addr = 0x3e, int_pin = 4)
    id.start()
