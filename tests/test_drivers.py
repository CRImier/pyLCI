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
    config_path = "tests/test_config.json"
except (ValueError, ImportError) as e:
    print("Absolute imports failed, trying relative imports")
    os.sys.path.append(os.path.dirname(os.path.abspath('.')))
    import main as main_py
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


if __name__ == '__main__':
    unittest.main()

