import pygame
from time import sleep

from skeleton import InputSkeleton

used_keys = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'UP', "DOWN", "LEFT", "RIGHT", "RETURN", "PAGEUP", "PAGEDOWN"]

#A dictionary to look up key names by their keycodes
keycode_mapping = dict([(getattr(pygame, "K_"+key_name), key_name) for key_name in used_keys])

class InputDevice(InputSkeleton):
    """ A driver for pygame-based keyboard key detection."""

    def __init__(self, path=None, name=None, **kwargs):
        """Initialises the ``InputDevice`` object.

        Kwargs:

            * ``path``: path to the input device. If not specified, you need to specify ``name``.
            * ``name``: input device name

        """
        InputSkeleton.__init__(self, mapping = [], **kwargs)

    def init_hw(self):
        return True

    def runner(self):
        """Blocking event loop which just calls supplied callbacks in the keymap."""
        try:
            while not self.stop_flag:
                #activeevent = pygame.ACTIVEEVENT
                #if activeevent != 1:
                #    print(activeevent)
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key in keycode_mapping:
                            key_name = "KEY_"+keycode_mapping[event.key]
                            if key_name == "KEY_RETURN": key_name = "KEY_ENTER"
                            self.send_key(key_name)
                sleep(0.01)
        except IOError as e:
            pass

    def atexit(self):
        InputSkeleton.atexit(self)
