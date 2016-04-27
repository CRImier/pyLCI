#!/usr/bin/env python
import os 
import json 

def read_config(config_path):
    try:
        with open(config_path, 'r') as f:
            data = json.load(f)
    except (IOError, ValueError) as e:
        raise
    else:
        return data
     
def write_config(config, config_path):
    try:
        with open(config_path, 'w') as f:
            data = json.dump(config, f)
    except (IOError, ValueError) as e:
        raise
    else:
        return data
     
if __name__ == "__main__":
    config = read_config("../config.json")
    print config
