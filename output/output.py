from helpers.config_parse import read_config
import importlib

#Currently only 16x2 char displays are fully supported and tested, as I simply don't have access to a bigger one yet -_-

if "__name__" != "__main__":
    config = read_config()
    output_config = config["output"][0]
    driver_name = output_config["driver"]
    driver_module = importlib.import_module("output.drivers."+driver_name)
    args = output_config["args"] if "args" in output_config else []
    kwargs = output_config["kwargs"] if "kwargs" in output_config else {}
    screen = driver_module.Screen(*args, **kwargs)
