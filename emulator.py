#!/usr/bin/env python

import logging
from multiprocessing import Process, Pipe
from time import sleep

import luma.emulator.device
import pygame
from luma.core.render import canvas


__EMULATOR_PROXY = None


def get_emulator():
    global __EMULATOR_PROXY
    if __EMULATOR_PROXY is None:
        __EMULATOR_PROXY = EmulatorProxy()
    return __EMULATOR_PROXY


class EmulatorProxy(object):
    def __init__(self):
        self.parent_conn, self.child_conn = Pipe()
        self.proc = Process(target=Emulator, args=(self.child_conn,))
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
        self.name = name

    def __call__(self, *args, **kwargs):
        self.parent_conn.send({
            'func_name': self.name,
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
            logging.info('Caught KeyboardIterrupt')
        except:
            logging.exception('Unknown exception during event loop')
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
            sleep(0.05)

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
            dims = (
                self.cursor_pos[0] - 1 + 2,
                self.cursor_pos[1] - 1,
                self.cursor_pos[0] + self.char_width + 2,
                self.cursor_pos[1] + self.char_height + 1,
            )

            if self.cursor_enabled:
                logging.debug('Drawing cursor with dims: %s', dims)
                draw.rectangle(dims, outline='white')

            args = args[:self.rows]
            logging.debug("type(args)=%s", type(args))

            for line, arg in enumerate(args):
                logging.debug('line %s: arg=%s, type=%s', line, arg, type(arg))
                # Emulator only:
                # Passing anything except a string to draw.text will cause
                # PIL to throw an exception.  Warn 'em here via the log.
                if not isinstance(arg, basestring):
                    logging.warning('emulator only likes strings fed to '
                        'draw.text, prepare for exception')
                y = (line * self.char_height - 1) if line != 0 else 0
                draw.text((2, y), arg, fill='white')
                logging.debug('after draw.text(2, %d), %s', y, arg)
