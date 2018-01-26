from time import sleep

import pygame

import emulator
from helpers import setup_logger
from skeleton import InputSkeleton

logger = setup_logger(__name__, "debug")

mapping = {'KEY_RETURN':'KEY_ENTER',
           'KEY_KP_ENTER':'KEY_ENTER',
           'KEY_KP_MULTIPLY':'KEY_ASTERISK',
           'KEY_KP_DIVIDE':'KEY_HASH',
           'KEY_MINUS':'KEY_HANGUP',
           'KEY_KP_MINUS':'KEY_HANGUP',
           'KEY_EQUALS':'KEY_ANSWER',
           'KEY_KP_PLUS':'KEY_ANSWER'
           }
USED_KEYS = [
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    'KP0', 'KP1', 'KP2', 'KP3', 'KP4', 'KP5', 'KP6', 'KP7', 'KP8', 'KP9',
    'UP', 'DOWN', 'LEFT', 'RIGHT', 'RETURN', 'PAGEUP', 'PAGEDOWN',
    'ASTERISK', 'HASH', 'PLUS', 'MINUS', 'EQUALS', 'F1', 'F2', 'F5', 'F6',
    'KP_MULTIPLY', 'KP_DIVIDE', 'KP_PLUS', 'KP_MINUS',
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
                logger.debug('Ignoring key %s' % key)
                continue
            key_name = 'KEY_' + KEY_MAP[key]
            key_name = mapping.get(key_name, key_name)

            if 'KP' in key_name:
                key_name = 'KEY_' + KEY_MAP[key].replace('KP', '')
            logger.debug('Mapped key %s' % key_name)

            self.send_key(key_name)

        self.emulator.quit()

    def atexit(self):
        InputSkeleton.atexit(self)
