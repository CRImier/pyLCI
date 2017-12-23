import logging
from time import sleep

import pygame

import emulator
from helpers.logger import setup_logger
from skeleton import InputSkeleton


logger = setup_logger(__name__, logging.WARNING)
USED_KEYS = [
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    'UP', 'DOWN', 'LEFT', 'RIGHT', 'RETURN', 'PAGEUP', 'PAGEDOWN'
]

KEY_MAP = dict([
    (getattr(pygame, 'K_' + key_name), key_name)
    for key_name in USED_KEYS
])


class InputDevice(InputSkeleton):
    """ A driver for pygame-based keyboard key detection."""

    def __init__(self, **kwargs):
        InputSkeleton.__init__(self, mapping=[], **kwargs)

    def init_hw(self):
        self.emulator = emulator.get_emulator()
        return True

    def runner(self):
        """
        Blocking event loop which just calls supplied callbacks in the keymap.
        """

        #TODO: debug and fix race condition
        while not hasattr(self, "emulator"):
            logger.debug("Input emulator not yet ready (a bug, TOFIX)")
            sleep(0.1)

        while not self.stop_flag:
            event = self.emulator.poll_input()
            if event is None:
                continue

            key = event['key']

            if key not in KEY_MAP:
                logging.debug('Ignoring key %s' % key)
                continue

            key_name = 'KEY_' + KEY_MAP[key]
            if key_name == 'KEY_RETURN':
                key_name = 'KEY_ENTER'
            logging.debug('Mapped key %s' % key_name)

            self.send_key(key_name)

        self.emulator.quit()

    def atexit(self):
        InputSkeleton.atexit(self)
