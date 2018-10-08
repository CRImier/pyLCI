#!/usr/bin/env python2
from __future__ import print_function

import json
import os
import shutil
from types import MethodType

from helpers.logger import setup_logger
logger = setup_logger(__name__, "warning")

def read_config(config_path):
    with open(config_path, 'r') as f:
        data = json.load(f)
    return data

def write_config(config_dict, config_path):
    with open(config_path, 'w') as f:
        json.dump(config_dict, f)

def read_or_create_config(config_path, default_config, app_name):
    # type: (str, str, str) -> dict
    """
    reads the config in `config_path` if invalid, replaces it with `default_config` and saves the erroneous config
    in `config_path`.failed. Also, if the config is a dictionary, adds keys to it if
    they're present in the default config but not in the current config.

    >>> print('{"configtype":"sample", "version":1}', file=open('/tmp/a_valid_config_file',"w"))
    >>> c = read_or_create_config("/tmp/a_valid_config_file", '{"default_config":true}', "test_runner")
    >>> c['configtype']
    u'sample'
    >>> c['default_config']
    True

    >>> print('{{{zzz', file=open('/tmp/a_invalid_config_file',"w"))
    >>> c = read_or_create_config("/tmp/a_invalid_config_file", '{"default_config":true}', "test_runner")
    >>> os.path.exists("/tmp/a_invalid_config_file.failed")
    True
    >>> c['default_config']
    True

    >>> print('{{{zzz', file=open('/tmp/a_invalid_config_file',"w"))
    >>> c = read_or_create_config("/tmp/a_invalid_config_file", '{"default_config":true}', "test_runner")
    >>> os.path.exists("/tmp/a_invalid_config_file.failed_1")
    True
    """
    try:
        config_dict = read_config(config_path)
    except (ValueError, IOError):
        logger.warning("{}: broken/nonexistent config, restoring with defaults...".format(app_name))
        if os.path.exists(config_path):
            counter = 1
            new_path = config_path + ".failed"
            while os.path.exists(new_path):
                new_path = config_path + ".failed_{}".format(counter)
                counter += 1
            logger.warning("Moving the faulty config file into {}".format(new_path))
            shutil.move(config_path, new_path)
        with open(config_path, 'w') as f:
            f.write(default_config)
        config_dict = read_config(config_path)
    default_config_obj = json.loads(default_config)
    keys_added = False
    if isinstance(default_config_obj, dict):
        for key, value in default_config_obj.items():
            if key not in config_dict.keys():
                config_dict[key] = value
                keys_added = True
                logger.debug("Adding key {} (from the default config) to the config for {}!".format(key, app_name))
        if keys_added:
            logger.warning("Added keys from default config to app {} - changes will not be preserved until the next time config is saved!".format(app_name))
    return config_dict

def save_config_gen(path):
    """
    A helper function, generates a "save config" function with the
    config path already set (to decrease verbosity)
    """
    def save_config(config):
        write_config(config, path)
    return save_config

def save_config_method_gen(obj, path, config_attr_name='config'):
    """
    A helper function, generates a "save config" method with the
    config path already set (to decrease verbosity) and the config
    attribute name hard-coded. This is the ``save_config_gen``
    equivalent for class-based apps.
    """
    def method(self):
        write_config(getattr(self, config_attr_name), path)
    return MethodType(method, obj)

if __name__ == "__main__":
    config = read_config("../config.json")
    print(config)
