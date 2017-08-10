from threading import Thread, Event
from time import sleep
from datetime import datetime

def activate_backlight_wrapper(func):
    def wrapper(self, *args, **kwargs):
        self.enable_backlight()
        self._backlight_active.set()
        result = func(self, *args, **kwargs)
        if self._backlight_interval and self._bl_thread is None:
            self.start_backlight_thread()
        return result
    return wrapper

def enable_backlight_wrapper(func):
    def wrapper(self, *args, **kwargs):
        if self._backlight_enabled == False:
            self._backlight_enabled = True
            return func(self, *args, **kwargs)
        return None
    return wrapper

def disable_backlight_wrapper(func):
    def wrapper(self, *args, **kwargs):
        if self._backlight_enabled == True:
            self._backlight_enabled = False
            return func(self, *args, **kwargs)
        return None
    return wrapper

class BacklightManager():
    _last_active = datetime.now()
    _backlight_enabled = False
    _backlight_active = Event()

    def init_backlight(self, backlight_active_level=True, backlight_pin = None, backlight_interval = None, **kwargs):
        self._backlight_active_level = backlight_active_level
        self._backlight_pin = backlight_pin
        if self._backlight_pin:
            import RPi.GPIO as GPIO
            self._bl_gpio = GPIO
            self._bl_gpio.setmode(self._bl_gpio.BCM)
            self._bl_gpio.setwarnings(False)
            self._bl_gpio.setup(self._backlight_pin, self._bl_gpio.OUT)
        self._backlight_interval = backlight_interval
        if self._backlight_interval:
            self.start_backlight_thread()

    def set_backlight_callback(self, obj):
        obj.backlight_cb = self.activate_backlight

    @activate_backlight_wrapper
    def activate_backlight(self):
        """Returns True when backlight has been activated, False if 
        backlight timer is disabled or backlight is already enabled"""
        return self._backlight_interval and self._bl_thread is None

    @enable_backlight_wrapper
    def enable_backlight(self):
        if self._backlight_pin:
            self._bl_gpio.output(self._backlight_pin, self._backlight_active_level)

    @disable_backlight_wrapper
    def disable_backlight(self):
        if self._backlight_pin:
            self._bl_gpio.output(self._backlight_pin, not self._backlight_active_level)

    def start_backlight_thread(self):
        self._bl_thread = Thread(target=self.backlight_manager, name="Screen backlight manager thread")
        self._bl_thread.daemon = True
        self._bl_thread.start()

    def backlight_manager(self):
        while True:
            if self._backlight_active.isSet():
                self._backlight_active.clear()
                self._last_active = datetime.now()
            elif (datetime.now() - self._last_active).total_seconds() >self._backlight_interval and self._backlight_enabled:
                self.disable_backlight()
                self._bl_thread = None
                return
            sleep(float(self._backlight_interval)/2) #Doesn't need to be done much often unless you need your backlight to be super precise. /2 is minimum though. 1 cycle to clear the flag and 1 cycle to disable backlight
