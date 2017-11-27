#!/usr/bin/env python
import os 
import json 

def read_config(config_path):
    with open(config_path, 'r') as f:
        data = json.load(f)
    return data
     
def write_config(config, config_path):
    with open(config_path, 'w') as f:
        json.dump(config, f)
     
def read_or_create_config(config_path, default_config, app_name):
    try:
        config = read_config(config_path)
    except (ValueError, IOError):
        print("{}: broken/nonexistent config, restoring with defaults...".format(app_name))
        with open(config_path, 'w') as f:
            f.write(default_config)
        config = read_config(config_path)
    return config

if __name__ == "__main__":
    config = read_config("../config.json")
    print config
