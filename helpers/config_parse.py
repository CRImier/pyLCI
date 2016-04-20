#!/usr/bin/env python
import os 
import json 

config_path = os.path.relpath("config.json")
config = None

def read_config(config_path=config_path):
    try:
        f = open(config_path, 'r')
        data = json.load(f)
        f.close()
    except (IOError, ValueError) as e:
        raise
    else:
        return data
     
if __name__ == "__main__":
    config = read_config()
    print config
