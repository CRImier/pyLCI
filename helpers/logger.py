#!/bin/env python2

import argparse
import logging
import os

from general import Singleton

try:
    import ConfigParser as configparser
except:
    import configparser  # python3


def setup_logger(logger_name, log_level):
    # type: (str, str) -> logging.Logger
    level = get_log_level(log_level, logging.WARNING)
    level = LoggingConfig().get_level(logger_name, level)
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    return logger


def get_log_level(log_level_name, default_value):
    # type: (str, int) -> int
    """
    Returns the log level based on a string name
    >>> get_log_level("warning", logging.ERROR) == logging.WARNING
    True
    >>> get_log_level("warning???", logging.ERROR) == logging.ERROR
    True
    """
    try:
        return logging._checkLevel(log_level_name.upper())
    except ValueError:
        return default_value


def get_log_level_name(level):
    assert type(level) == int
    if level in logging._levelNames:
        return logging._levelNames[level]
    return logging.NOTSET


def on_reload(*args):
    LoggingConfig().reload_config()


class LoggingConfig(Singleton):
    def __init__(self):
        self.default_log_level = logging.WARNING
        self._config_file_path = "/opt/zpui/log_conf.ini"
        self._app_overrides = {}
        self._load_config()

    def get_level(self, app_name, value_if_not_found=None):
        if not value_if_not_found:
            value_if_not_found = self.default_log_level
        return_value = value_if_not_found

        if app_name in self._app_overrides:
            return_value = self._app_overrides[app_name]

        return return_value

    def set_level(self, app_name, level):
        self._app_overrides[app_name] = get_log_level(level, logging.WARNING)
        self._dispatch_log_levels()
        self.save_to_config()

    def _load_config(self):
        if not os.path.exists(self._config_file_path):
            open(self._config_file_path, 'a+').close()
            return
        ini_parser = configparser.ConfigParser()
        ini_parser.read(self._config_file_path)

        if ini_parser.has_section("global"):
            level_name = ini_parser.get("global", "default_level")
            self.default_log_level = get_log_level(level_name, logging.WARNING)
        if ini_parser.has_section("app_override"):
            for override in ini_parser.items("app_override"):
                self._app_overrides[override[0]] = get_log_level(override[1], logging.NOTSET)

    def reload_config(self):
        """
        Loads the config file once again, reading and applying all config level
        overrides found in it.
        """
        self._load_config()
        self._dispatch_log_levels()

    def __str__(self):
        config_str = "default log level: {}".format(logging.getLevelName(self.default_log_level))
        if not len(self._app_overrides):
            config_str += "\n\tConfig file absent or empty"
        else:
            for app_name, level in self._app_overrides.items():
                config_str += "\n\t{} : {}".format(app_name, get_log_level_name(level))
        return config_str

    def _dispatch_log_levels(self):
        for app_name, level in self._app_overrides.items():
            logging.getLogger(app_name).setLevel(level)
            for h in logging.getLogger(app_name).handlers:
                h.setLevel(level)


    def save_to_config(self):
        ini_parser = configparser.ConfigParser()
        ini_parser.add_section("app_override")
        ini_parser.add_section("global")
        ini_parser.set("global", "default_level", get_log_level_name(self.default_log_level))
        for app_name, level in self._app_overrides.items():
            ini_parser.set("app_override", app_name, get_log_level_name(level))
        with open(self._config_file_path, 'w+') as config_file:
            ini_parser.write(config_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="ZPUI logger configurator")
    subparsers = parser.add_subparsers(dest='cmd', help="Command")
    subparsers.add_parser('show', help="Shows the current configuration")
    set_parser = subparsers.add_parser('set', help="Changes the log level of a given app")
    set_parser.add_argument('--name', dest='app_name', type=str, required=True)
    set_parser.add_argument('--level', dest='level', type=str, required=True)

    args = parser.parse_args()
    config = LoggingConfig()
    if args.cmd == 'show':
        print(config)

    if args.cmd == 'set':
        config.set_level(args.app_name, args.level)
