"""tests output and input drivers and config parsing"""
import os
import json
import unittest
import traceback
from copy import copy
from threading import Event
from mock import patch, Mock

try:
    import main as main_py
    from input.drivers import test_input
    config_path = "tests/test_config.json"
except (ValueError, ImportError) as e:
    print("Absolute imports failed, trying relative imports")
    os.sys.path.append(os.path.dirname(os.path.abspath('.')))
    import main as main_py
    from input.drivers import test_input
    config_path = "test_config.json"


with open(config_path, 'r') as f:
    base_config = json.load(f)


class TestDrivers(unittest.TestCase):
    """Tests various drivers. Mostly tests various config permutations, as well as
    base drivers like ``luma_driver.py``, `input.init()` and `output.init()`."""

    def test_sh1106(self):
        output_config = {"driver":"sh1106", "kwargs":{"hw":"dummy"}}
        config = copy(base_config)
        config["output"][0] = output_config
        with patch.object(main_py, 'load_config') as mocked:
            mocked.return_value = (config, "test_config.json")
            i, o = main_py.init()
        assert(isinstance(i, main_py.input.InputProxy))
        assert(isinstance(o, main_py.output.OutputProxy))

    def test_ssd1306(self):
        output_config = {"driver":"ssd1306", "kwargs":{"hw":"dummy"}}
        config = copy(base_config)
        config["output"][0] = output_config
        with patch.object(main_py, 'load_config') as mocked:
            mocked.return_value = (config, "test_config.json")
            i, o = main_py.init()
        assert(isinstance(i, main_py.input.InputProxy))
        assert(isinstance(o, main_py.output.OutputProxy))

    def test_st7735(self):
        output_config = {"driver":"st7735", "kwargs":{"hw":"dummy"}}
        config = copy(base_config)
        config["output"][0] = output_config
        with patch.object(main_py, 'load_config') as mocked:
            mocked.return_value = (config, "test_config.json")
            i, o = main_py.init()
        assert(isinstance(i, main_py.input.InputProxy))
        assert(isinstance(o, main_py.output.OutputProxy))

    def test_st7735_with_params(self):
        output_config = {"driver":"st7735", "kwargs":{"hw":"dummy", "rotate":1, \
                         "h_offset":1, "v_offset":2, "height":160}}
        config = copy(base_config)
        config["output"][0] = output_config
        with patch.object(main_py, 'load_config') as mocked:
            mocked.return_value = (config, "test_config.json")
            i, o = main_py.init()
        assert(isinstance(i, main_py.input.InputProxy))
        assert(isinstance(o, main_py.output.OutputProxy))
        assert(o.height == 160)

    def test_sh1106_with_backlight(self):
        output_config = {"driver":"sh1106", "kwargs":{"hw":"dummy", "backlight_interval":10}}
        config = copy(base_config)
        config["output"][0] = output_config
        with patch.object(main_py, 'load_config') as mocked:
            mocked.return_value = (config, "test_config.json")
            i, o = main_py.init()
        assert(isinstance(i, main_py.input.InputProxy))
        assert(isinstance(o, main_py.output.OutputProxy))

    def test_two_input_drivers(self):
        config = copy(base_config)
        config["input"].append(config["input"][0])
        with patch.object(main_py, 'load_config') as mocked:
            mocked.return_value = (config, "test_config.json")
            i, o = main_py.init()
        assert(isinstance(i, main_py.input.InputProxy))
        assert(isinstance(o, main_py.output.OutputProxy))
        # there was a problem with input.init() not registering multiple drivers
        # when they're made from the same driver (and have the same name)
        assert(len(main_py.input_processor.drivers) == 2)
        # so that no ugly exception is raised when the test finishes
        main_py.input_processor.atexit()

    def test_input_driver_attach_detach(self):
        config = copy(base_config)
        with patch.object(main_py, 'load_config') as mocked:
            mocked.return_value = (config, "test_config.json")
            i, o = main_py.init()
        name = "test_input-1"
        assert(len(main_py.input_processor.drivers) == 1)
        main_py.input_processor.attach_driver(test_input.InputDevice(), name)
        assert(len(main_py.input_processor.drivers) == 2)
        main_py.input_processor.detach_driver(name)
        assert(len(main_py.input_processor.drivers) == 1)
        # so that no ugly exception is raised when the test finishes
        main_py.input_processor.atexit()

if __name__ == '__main__':
    unittest.main()

