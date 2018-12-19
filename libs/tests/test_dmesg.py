"""tests for the dmesg library"""
import os
import unittest
import traceback

from mock import patch, Mock

try:
    from libs import dmesg
except (ValueError, ImportError) as e:
    print("Absolute imports failed, trying relative imports")
    os.sys.path.append(os.path.dirname(os.path.abspath('.')))
    # Store original __import__
    orig_import = __import__

    def import_mock(name, *args, **kwargs):
        if name in ['helpers'] and not kwargs:
            #Have to filter for kwargs since there's a package in 'json'
            #that calls __builtins__.__import__ with keyword arguments
            #and we don't want to mock that call
            return Mock()
        return orig_import(name, *args, **kwargs)

    #with patch('__builtin__.__import__', side_effect=import_mock):
    import dmesg

test_dir = os.path.dirname(os.path.abspath(__file__))

def local_path(path):
    return os.path.join(test_dir, path)


class TestDmesg(unittest.TestCase):
    def test_esp_overflown_trace(self):
        """Tests wheth"""
        with open(local_path("esp_overflown.txt")) as f:
            output = f.read()
        msgs = dmesg.parse_dmesg_output(output)
        assert(len(msgs) == 1897)
        assert(dmesg.dmesg_output_was_truncated(msgs) == True)

    def test_esp_broken_trace(self):
        with open(local_path("esp_broken_trace.txt")) as f:
            output = f.read()
        msgs = dmesg.parse_dmesg_output(output)
        assert(dmesg.dmesg_output_was_truncated(msgs) == False)
        assert(len(msgs) == 1025)

    def test_esp_driver_crash(self):
        with open(local_path("esp_driver_crash.txt")) as f:
            output = f.read()
        msgs = dmesg.parse_dmesg_output(output)
        assert(dmesg.dmesg_output_was_truncated(msgs) == True)
        assert(len(msgs) == 128)

    def test_esp_driver_working(self):
        with open(local_path("esp_driver_working.txt")) as f:
            output = f.read()
        msgs = dmesg.parse_dmesg_output(output)
        assert(dmesg.dmesg_output_was_truncated(msgs) == False)
        assert(len(msgs) == 250)

if __name__ == '__main__':
    unittest.main()

