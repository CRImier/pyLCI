from helpers.config_parse import read_config
import importlib

#Currently only 16x2 char displays are fully supported and tested, as I simply don't have access to a bigger one yet -_-

if "__name__" != "__main__":
    config = read_config()
    driver_name = config["output"][0]["driver"]
    driver_module = importlib.import_module("output.drivers."+driver_name)
    try:
        driver_args = config["output"][0]["driver_args"]
    except KeyError:
        driver_args = []
    try:
        driver_kwargs = config["output"][0]["driver_kwargs"]
    except KeyError:
        driver_kwargs = {}
    screen = driver_module.Screen(*driver_args, **driver_kwargs)
