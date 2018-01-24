#!/usr/bin/env python2

import argparse
import logging
import os
import signal
import sys
import threading
import traceback
from logging.handlers import RotatingFileHandler

from apps.app_manager import AppManager
from context_manager import ContextManager
from helpers import read_config, local_path_gen
from input import input
from output import output
from ui import Printer
import helpers.logger

emulator_flag_filename = "emulator"
local_path = local_path_gen(__name__)
is_emulator = emulator_flag_filename in os.listdir(".")

logging_path = local_path('zpui.log')
logging_format = (
    '[%(levelname)s] %(asctime)s %(name)s: %(message)s',
    '%Y-%m-%d %H:%M:%S'
)

config_paths = ['/boot/zpui_config.json', '/boot/pylci_config.json'] if not is_emulator else []
config_paths.append(local_path('config.json'))
#Using the .example config as a last resort
config_paths.append(local_path('default_config.json'))

input_processor = None
screen = None
cm = None
config = None
config_path = None

def init():
    """Initialize input and output objects"""

    global input_processor, screen, cm, config, config_path
    config = None

    # Load config
    for config_path in config_paths:
        #Only try to load the config file if it's present
        #(unclutters the logs)
        if os.path.exists(config_path):
            try:
                logging.debug('Loading config from {}'.format(config_path))
                config = read_config(config_path)
            except:
                logging.exception('Failed to load config from {}'.format(config_path))
            else:
                logging.info('Successfully loaded config from {}'.format(config_path))
                break
    # After this loop, the config_path global should contain
    # path for config that successfully loaded

    if config is None:
        sys.exit('Failed to load any config files!')

    # Initialize output
    try:
        screen = output.init(config['output'])
    except:
        logging.exception('Failed to initialize the output object')
        logging.exception(traceback.format_exc())
        sys.exit(2)

    # Initialize the context manager
    cm = ContextManager()

    # Initialize input
    try:
        # Now we can show errors on the display
        input_processor = input.init(config["input"], cm)
    except:
        logging.exception('Failed to initialize the input object')
        logging.exception(traceback.format_exc())
        Printer(['Oops. :(', 'y u make mistake'], None, screen, 0)
        sys.exit(3)

    # Tying objects together
    if hasattr(screen, "set_backlight_callback"):
        screen.set_backlight_callback(input_processor)
    cm.init_io(input_processor, screen)
    cm.switch_to_context("main", launch_thread=False)
    i, o = cm.get_io_for_context("main")

    return i, o


def launch(name=None, **kwargs):
    """
    Launches ZPUI, either in full mode or in
    single-app mode (if ``name`` kwarg is passed).
    """

    i, o = init()
    appman_config = config.get("app_manager", {})
    app_man = AppManager('apps', cm, config=appman_config)

    if name is None:
        try:
            from splash import splash
            splash(i, o)
        except:
            logging.exception('Failed to load the splash screen')
            logging.exception(traceback.format_exc())

        # Load all apps
        app_menu = app_man.load_all_apps()
        runner = app_menu.activate
    else:
        # If using autocompletion from main folder, it might
        # append a / at the name end, which isn't acceptable
        # for load_app
        name = name.rstrip('/')

        # Load only single app
        try:
            app_path = app_man.get_app_path_for_cmdline(name)
            app = app_man.load_app(app_path)
        except:
            logging.exception('Failed to load the app: {0}'.format(name))
            input_processor.atexit()
            raise
        cm.switch_to_context(app_path, launch_thread=False)
        runner = app.on_start if hasattr(app, "on_start") else app.callback

    exception_wrapper(runner)


def exception_wrapper(callback):
    """
    This is a wrapper for all applications and menus.
    It catches exceptions and stops the system the right
    way when something bad happens, be that a Ctrl+c or
    an exception in one of the applications.
    """
    status = 0
    try:
        callback()
    except KeyboardInterrupt:
        logging.info('Caught KeyboardInterrupt')
        Printer(["Does Ctrl+C", "hurt scripts?"], None, screen, 0)
        status = 1
    except:
        logging.exception('A wild exception appears!')
        logging.exception(traceback.format_exc())
        Printer(["A wild exception", "appears!"], None, screen, 0)
        status = 1
    else:
        logging.info('Exiting ZPUI')
        Printer("Exiting ZPUI", None, screen, 0)
    finally:
        input_processor.atexit()
        sys.exit(status)


def dump_threads(*args):
    """
    Helpful signal handler for debugging threads
    """

    logger.critical('\nSIGUSR received, dumping threads!\n')
    for th in threading.enumerate():
        logger.critical(th)
        log = traceback.format_stack(sys._current_frames()[th.ident])
        for frame in log:
            logger.critical(frame)


if __name__ == '__main__':
    """
    Parses arguments, initializes logging, launches ZPUI
    """

    # Signal handler for debugging
    signal.signal(signal.SIGUSR1, dump_threads)
    signal.signal(signal.SIGHUP, helpers.logger.on_reload)

    # Setup argument parsing
    parser = argparse.ArgumentParser(description='ZPUI runner')
    parser.add_argument(
        '--app',
        '-a',
        help='Launch ZPUI with a single app loaded (useful for testing)',
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
    formatter = logging.Formatter(*logging_format)

    # Rotating file logs (for debugging crashes)
    rotating_handler = RotatingFileHandler(
        logging_path,
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

    # Launch ZPUI
    launch(**vars(args))
