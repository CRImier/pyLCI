from time import sleep
from threading import Event

from ui import Canvas
from ui.base_ui import BaseUIElement
from apps import ZeroApp
from helpers import ExitHelper, setup_logger, remove_left_failsafe, read_or_create_config, local_path_gen, save_config_method_gen

local_path = local_path_gen(__name__)
logger = setup_logger(__name__, "info")

settings = {"name":"KeyScreen"}

class LockApp(ZeroApp):
    locked = False

    def set_context(self, c):
        self.context = c
        c.threaded = True
        c.set_target(self.activate_lockscreen)
        c.register_action("lock_screen", c.request_switch, "Lock screen", description="Switches to the lockscreen app")

    def get_screens(self):
        return {"KeyScreen": KeyScreen,
                "PinScreen": PinScreen}

    def activate_lockscreen(self):
        if not self.context.request_exclusive():
            logger.info("Can't get exclusive access!")
            return False #Couldn't get exclusive access!
        screens = self.get_screens()
        self.locked = True
        c = Canvas(self.o)
        c.centered_text("Locked")
        remove_left_failsafe(self.i)
        while self.locked:
            c.display()
            lockscreen_obj = screens.get(settings["name"], KeyScreen)
            args = settings.get("args", [])
            kwargs = settings.get("kwargs", {})
            lockscreen = lockscreen_obj(self.i, self.o, *args, **kwargs)
            lockscreen.wait_loop()
            logger.info("Lockscreen triggered")
            self.locked = lockscreen.activate()
            logger.info("Finished, restarting loop")
        self.context.rescind_exclusive()

class KeyScreen(BaseUIElement):
    sleep_time = 0.1
    default_key_sequence = ["KEY_ENTER", "KEY_*"]

    def __init__(self, i, o, timeout=3, key_sequence=None):
        self.key_sequence = key_sequence if key_sequence else self.default_key_sequence
        self.key_sequence_position = 0
        self._locked = Event()
        self.timeout = timeout
        self.reset_timeout()
        BaseUIElement.__init__(self, i, o, name="KeyScreen lockscreen")

    def wait_loop(self):
        self.eh = ExitHelper(self.i, keys="*").start()
        while self.eh.do_run():
            sleep(self.sleep_time)

    def before_activate(self):
        self.locked = True
        self.key_sequence_position = 0
        if self.eh.last_key == self.key_sequence[0]:
            self.key_sequence_position += 1
            self.check_locked()

    def check_locked(self):
        if len(self.key_sequence) == self.key_sequence_position:
            self.unlock()

    def receive_key(self, key):
        if key == self.key_sequence[self.key_sequence_position]:
            self.key_sequence_position += 1
            self.check_locked()
        else:
            self.deactivate()

    def get_return_value(self):
        return self.locked

    def idle_loop(self):
        self.check_timeout()
        sleep(self.sleep_time)

    @property
    def is_active(self):
        return self.in_foreground and self.locked

    @property
    def locked(self):
        return self._locked.isSet()

    @locked.setter
    def locked(self, value):
        self._locked.set() if value else self._locked.clear()

    def reset_timeout(self):
        self.timeout_counter = 0

    def check_timeout(self):
        self.timeout_counter += 1
        if self.timeout_counter * self.sleep_time > self.timeout:
            logger.info("Timed out")
            self.deactivate()

    def unlock(self):
        self.locked = False

    def set_first_key_press(self):
        self.first_key_pressed = True
        self.refresh()

    def generate_keymap(self):
        return {}

    def configure_input(self):
        self.i.set_streaming(self.receive_key)

    def refresh(self):
        c = Canvas(self.o)
        charheight = 16
        font = c.load_font("Fixedsys62.ttf", charheight)
        key_name = self.key_sequence[self.key_sequence_position][len("KEY_"):]
        c.centered_text("Press {}".format(key_name.lower().capitalize()), font=font)
        self.o.display_image(c.get_image())


class PinScreen(object):
    accepted_keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "*", "#"]
    sleep_time = 0.1

    def __init__(self, i, o, pin, timeout=3):
        self.pin = pin
        self.i = i
        self.o = o
        self.timeout = timeout
        self.reset_timeout()
        self.locked = Event()
        self.active = Event()
        self.clear()

    def wait_loop(self):
        eh = ExitHelper(self.i, keys="*").start()
        while eh.do_run():
            sleep(self.sleep_time)

    def activate(self):
        self.set_keymap()
        self.active.set()
        self.locked.set()
        self.refresh()
        while self.active.isSet() and self.locked.isSet():
            self.check_timeout()
            sleep(self.sleep_time)
        return self.locked.isSet()

    def reset_timeout(self):
        self.timeout_counter = 0

    def check_timeout(self):
        self.timeout_counter += 1
        if self.timeout_counter * self.sleep_time > self.timeout:
            logger.info("Timed out")
            self.deactivate()

    def deactivate(self):
        self.clear()
        self.active.clear()

    def clear(self):
        self.value = []

    def set_keymap(self):
        keymap = {"KEY_LEFT": self.backspace}
        self.i.stop_listen()
        self.i.set_keymap(keymap)
        self.i.set_streaming(self.receive_key)
        self.i.listen()

    def receive_key(self, key):
        if not self.active.isSet():
            return
        self.reset_timeout()
        if key.startswith("KEY_"):
            value = key[4:]
            if value in self.accepted_keys:
                self.add_character(value)

    def backspace(self):
        if self.value:
            self.value = self.value[:-1]
        self.refresh()

    def add_character(self, character):
        if len(self.value) < len(self.pin):
            self.value.append(character)
            self.refresh()
        if len(self.value) == len(self.pin):
            self.check_password()

    def check_password(self):
        if self.pin == "".join(self.value):
            logger.info("Password correct!")
            self.locked.clear()
        else:
            self.value = []
            self.refresh()

    def refresh(self):
        c = Canvas(self.o)
        charwidth = 20
        charheight = 32
        font = c.load_font("Fixedsys62.ttf", charheight)
        pin_width = len(self.pin)*charwidth
        x_offset = (self.o.width-pin_width)/2
        y_offset = 15
        c.line((x_offset, y_offset+charheight, str(-x_offset), y_offset+charheight))
        c.line((x_offset, y_offset+charheight, x_offset, y_offset+charheight-5))
        for x in range(len(self.pin)):
            i = x+1
            if x in range(len(self.value)):
                c.text("*", (x_offset+charwidth*x, y_offset), font=font)
            c.line((x_offset+charwidth*i, y_offset+charheight, x_offset+charwidth*i, y_offset+charheight-5))
        self.o.display_image(c.get_image())


class LockscreenSettings(object):
    menu_name = "Lockscreen"

    def __init__(self, i, o):
        self.i = i
        self.o = o
        self.config = read_or_create_config(local_path("config.json"), '{"lockscreen_type":"KeyScreen"}', "Lockscreen app config")
        self.save_config = save_config_method_gen(self, local_path("ls_config.json"))
        self.current_screen = None # Need to continue writing this

    def update_settings(self):
        settings["name"] = self.config.get("lockscreen_type", "KeyScreen")
        settings["args"] = self.config.get("lockscreen_args", [])
        settings["kwargs"] = self.config.get("lockscreen_kwargs", {})

    def get_settings(self):
        contents = [["Type", self.change_type]]

        # TODO: append settings for each screen

    def activate(self):
        Menu([], self.i, self.o, name="Lockscreen settings menu", contents_hook=self.get_settings).activate()


LockscreenSettings(None, None).update_settings()
