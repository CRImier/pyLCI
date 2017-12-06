#!/usr/bin/env python2
from __future__ import print_function
import json


def read_config(config_path):
    with open(config_path, 'r') as f:
        data = json.load(f)
    return data


def write_config(config_dict, config_path):
    with open(config_path, 'w') as f:
        json.dump(config_dict, f)


def read_or_create_config(config_path, default_config, app_name):
    try:
        config_dict = read_config(config_path)
    except (ValueError, IOError):
        print("{}: broken/nonexistent config, restoring with defaults...".format(app_name))
        with open(config_path, 'w') as f:
            f.write(default_config)
        config_dict = read_config(config_path)
    return config_dict


if __name__ == "__main__":
    config = read_config("../config.json")
    print(config)
