#!/usr/bin/env python2

from multiprocessing import Process, Pipe
from time import sleep

import luma.emulator.device
import pygame
from luma.core.render import canvas

from helpers import setup_logger
from output.output import GraphicalOutputDevice, CharacterOutputDevice

logger = setup_logger(__name__, "warning")

__EMULATOR_PROXY = None


def get_emulator():
    global __EMULATOR_PROXY
    if __EMULATOR_PROXY is None:
        __EMULATOR_PROXY = EmulatorProxy()
    return __EMULATOR_PROXY


class EmulatorProxy(object):

    width = 128
    height = 64
    device_mode = "1"
    char_width = 6
    char_height = 8
    type = ["char", "b&w-pixel"]

    def __init__(self):
        self.device = type("MockDevice", (), {"mode":"1", "size":(128, 64)})
        self.parent_conn, self.child_conn = Pipe()
        self.proc = Process(target=Emulator, args=(self.child_conn,))
        self.__base_classes__ = (GraphicalOutputDevice, CharacterOutputDevice)
        self.current_image = None
        self.proc.start()

    def poll_input(self, timeout=1):
        if self.parent_conn.poll(timeout) is True:
            return self.parent_conn.recv()
        return None

    def quit(self):
        DummyCallableRPCObject(self.parent_conn, 'quit')()
        self.proc.join()

    def __getattr__(self, name):
        # Raise an exception if the attribute being called
        # Doesn't actually exist on the Emulator object
        getattr(Emulator, name)
        return DummyCallableRPCObject(self.parent_conn, name)


class DummyCallableRPCObject(object):
    def __init__(self, parent_conn, name):
        self.parent_conn = parent_conn
        self.__name__ = name

    def __call__(self, *args, **kwargs):
        self.parent_conn.send({
            'func_name': self.__name__,
            'args': args,
            'kwargs': kwargs
        })


class Emulator(object):
    def __init__(self, child_conn):
        self.child_conn = child_conn

        self.char_width = 6
        self.char_height = 8

        self.cols = 128 / self.char_width
        self.rows = 64 / self.char_height

        self.cursor_enabled = False
        self.cursor_pos = [0, 0]
        self._quit = False

        emulator_attributes = {
            'display': 'pygame',
            'width': 128,
            'height': 64,
        }

        Device = getattr(luma.emulator.device, 'pygame')
        self.device = Device(**emulator_attributes)

        try:
            self._event_loop()
        except KeyboardInterrupt:
            logger.info('Caught KeyboardIterrupt')
        except:
            logger.exception('Unknown exception during event loop')
            raise
        finally:
            self.child_conn.close()

    def _poll_input(self):
        event = pygame.event.poll()
        if event.type == pygame.KEYDOWN:
            self.child_conn.send({'key': event.key})

    def _poll_parent(self):
        if self.child_conn.poll() is True:
            event = self.child_conn.recv()
            func = getattr(self, event['func_name'])
            func(*event['args'], **event['kwargs'])

    def _event_loop(self):
        while self._quit is False:
            self._poll_parent()
            self._poll_input()
            sleep(0.001)

    def setCursor(self, row, col):
        self.cursor_pos = [
            col * self.char_width,
            row * self.char_height,
        ]

    def quit(self):
        self._quit = True

    def noCursor(self):
        self.cursor_enabled = False

    def cursor(self):
        self.cursor_enabled = True

    def display_data(self, *args):
        with canvas(self.device) as draw:

            if self.cursor_enabled:
                logger.debug('Drawing cursor with dims: %s', dims)
                dims = (
                    self.cursor_pos[0] - 1 + 2,
                    self.cursor_pos[1] - 1,
                    self.cursor_pos[0] + self.char_width + 2,
                    self.cursor_pos[1] + self.char_height + 1,
                )
                draw.rectangle(dims, outline='white')

            args = args[:self.rows]
            logger.debug("type(args)=%s", type(args))

            for line, arg in enumerate(args):
                logger.debug('line %s: arg=%s, type=%s', line, arg, type(arg))
                # Emulator only:
                # Passing anything except a string to draw.text will cause
                # PIL to throw an exception.  Warn 'em here via the log.
                if not isinstance(arg, basestring):
                    raise ValueError("*args[{}] is not a string, but a {} - unacceptable!".format(line, type(arg)))
                y = (line * self.char_height - 1) if line != 0 else 0
                draw.text((2, y), arg, fill='white')
                logger.debug('after draw.text(2, %d), %s', y, arg)

    def display_image(self, image):
        self.device.display(image)
