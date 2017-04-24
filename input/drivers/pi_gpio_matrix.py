from time import sleep

from skeleton import InputSkeleton

class InputDevice(InputSkeleton):

    default_mapping = [
    ["KEY_1", "KEY_UP", "KEY_3"],
    ["KEY_LEFT", "KEY_ENTER", "KEY_RIGHT"],
    ["KEY_7", "KEY_DOWN", "KEY_9"],
    ["KEY_*", "KEY_0", "KEY_#"]]

    def __init__(self, cols=[5, 6, 13], rows=[12, 16, 20, 21], **kwargs):
        """Initialises the ``InputDevice`` object. 

        Kwargs:
        
        * ``button_pins``: GPIO mubers which to treat as buttons (GPIO.BCM numbering)
        * ``debug``: enables printing button press and release events when set to True
        """
        self.cols = cols
        self.rows = rows
        InputSkeleton.__init__(self, **kwargs)

    def init_hw(self):
        import RPi.GPIO as GPIO #Doing that because I couldn't mock it for ReadTheDocs
        self.GPIO = GPIO
        GPIO.setmode(GPIO.BCM) 
        for pin_num in self.rows:
            GPIO.setup(pin_num, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        for pin_num in self.cols:
            GPIO.setup(pin_num, GPIO.OUT)
            GPIO.output(pin_num, True)
        self.button_states = [[False for u in range(len(self.cols))] for i in range(len(self.rows))]

    def runner(self):
        """Polling loop. Stops when ``stop_flag`` is set to True."""
        while not self.stop_flag:
            for row_num, row_pin in enumerate(self.rows):
                prev_row_state = self.button_states[row_num]
                if self.GPIO.input(row_pin) != any(prev_row_state):
                    self.GPIO.setup(row_pin, self.GPIO.IN, pull_up_down=self.GPIO.PUD_UP)
                    #A button pressed!
                    col_num = None
                    for col_num, col_pin in enumerate(self.cols):
                        self.GPIO.output(col_pin, False)
                        state = not self.GPIO.input(row_pin)
                        self.GPIO.output(col_pin, True)
                        prev_state = self.button_states[row_num][col_num]
                        if state == True and prev_state == False:
                            key = self.mapping[row_num][col_num]
                            self.send_key(key)
                        self.button_states[row_num][col_num] = state
                    self.GPIO.setup(row_pin, self.GPIO.IN, pull_up_down=self.GPIO.PUD_DOWN)
            sleep(0.01)



if __name__ == "__main__":
    id = InputDevice(threaded=False)
    id.runner()
