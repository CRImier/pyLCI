#!/usr/bin/env python

import argparse
import logging
import os
import signal
import sys
import threading
import traceback

from logging.handlers import RotatingFileHandler
from subprocess import call
from time import sleep

from apps.app_manager import AppManager
from helpers import read_config
from input import input
from output import output
from splash import splash
from ui import Printer, Menu


LOGGING_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'pylci.log'
)

LOGGING_FMT = (
    '[%(levelname)s] %(asctime)s %(filename)s [%(process)d]: %(message)s',
    '%Y-%m-%d %H:%M:%S'
)

CONFIG_PATHS = [
    '/boot/pylci_config.json',
    './config.json'
]


def init():
    """
    Initialize input and output objects
    """

    config = None

    # Load config
    for path in CONFIG_PATHS:
        try:
            logging.debug('Loading config from {0}'.format(path))
            config = read_config(path)
        except:
            logging.exception('Failed to load config')
        else:
            logging.debug('Successfully loaded config')
            break

    if config is None:
        sys.exit('Failed to load any config file')

    # Initialize output
    try:
        output.init(config['output'])
        o = output.screen
    except:
        logging.exception('Failed to initialize the output object')
        raise

    # Initialize input
    try:
        # Now we can show errors on the display
        input.init(config['input'])
        i = input.listener
    except:
        logging.exception('Failed to initialize the input object')
        Printer(['Oops. :(', 'y u make mistake'], None, o, 0)
        raise

    return i, o


def launch(name=None, **kwargs):
    """
    Launches pyLCI, either in full mode or in
    single-app mode (if ``name`` kwarg is passed).
    """

    i, o = init()
    app_man = AppManager('apps', Menu, Printer, i, o)

    if name is None:
        try:
            splash(i, o)
        except:
            logging.exception('Failed to load the splash screen')

        # Load all apps
        app_menu = app_man.load_all_apps()
        app_entry = app_menu.activate
    else:
        # If using autocompletion from main folder, it might
        # append a / at the name end, which isn't acceptable
        # for load_app
        name = name.rstrip('/')

        # Load only single app
        try:
            app = app_man.load_app(name)
        except:
            logging.exception('Failed to load the app: {0}'.format(name))
            i.atexit()
            raise
        app_entry = app.callback

    exception_wrapper(app_entry, i, o)


def exception_wrapper(callback, i, o):
    """
    This is a wrapper for all applications and menus.
    It catches exceptions and stops the system the right
    way when something bad happens, be that a Ctrl+c or
    an exception in one of the applications.
    """

    try:
        callback()
    except KeyboardInterrupt:
        logging.info('Caught KeyboardInterrupt')
        Printer(["Does Ctrl+C", "hurt scripts?"], None, o, 0)
        i.atexit()
        sys.exit(1)
    except:
        logging.exception('A wild exception appears!')
        Printer(["A wild exception", "appears!"], None, o, 0)
        i.atexit()
        sys.exit(1)
    else:
        logging.info('Exiting pyLCI')
        Printer("Exiting pyLCI", None, o, 0)
        i.atexit()
        sys.exit(0)


def dumpthreads(*args):
    """
    Helpful signal handler for debugging threads
    """

    print('\nSIGUSR received, dumping threads\n')
    for th in threading.enumerate():
        print(th)
        traceback.print_stack(sys._current_frames()[th.ident])
        print('')


if __name__ == '__main__':
    """
    Parses arguments, initializes logging, launches pyLCI
    """

    # Signal handler for debugging
    signal.signal(signal.SIGUSR1, dumpthreads)

    # Setup argument parsing
    parser = argparse.ArgumentParser(description='pyLCI runner')
    parser.add_argument(
        '--app',
        '-a',
        help='Launch pyLCI with a single app loaded (useful for testing)',
        dest='name',
        default=None)
    parser.add_argument(
        '--log-level',
        '-l',
        help='The minimum log level to output',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO')
    args = parser.parse_args()

    # Setup logging
    logger = logging.getLogger()
    formatter = logging.Formatter(*LOGGING_FMT)

    # Rotating file logs (for debugging crashes)
    rotating_handler = RotatingFileHandler(
        LOGGING_PATH,
        maxBytes=10000,
        backupCount=5)
    rotating_handler.setFormatter(formatter)
    logger.addHandler(rotating_handler)

    # Live console logging
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Set log level
    logger.setLevel(args.log_level)

    # Launch pyLCI
    launch(**vars(args))
