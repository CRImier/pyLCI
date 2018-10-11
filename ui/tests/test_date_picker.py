"""Test for the ui element DatePicker"""
import os, unittest

from mock import patch, Mock

try:
	from ui import DatePicker
except ImportError:
	print("Absolute imports failed, trying relative imports")
	os.sys.path.append(os.path.dirname(os.path.abspath('.')))
	# Store original __import__
	orig_import = __import__

	def import_mock(name, *args):
		if name in ['helpers']:
			return Mock()
		elif name == 'ui.utils':
			import utils
			return utils
		return orig_import(name, *args)

	with patch('__builtin__.__import__', side_effect=import_mock):
		from date_picker import DatePicker

def get_mock_input():
	return Mock()

def get_mock_output(width=128, height=64, mode="1"):
    m = Mock()
    m.configure_mock(width=width, height=height, device_mode=mode, type=["b&w-pixel"])
    return m

dp_name = "Test DatePicker"

class TestDatePicker(unittest.TestCase):
	"""Tests DatePicker"""

	def test_constructor(self):
		"""Tests constructor"""
		dp = DatePicker(get_mock_input(), get_mock_output(), name=dp_name)
		self.assertIsNotNone(dp)

	def test_keymap(self):
		"""Tests keymap"""
		dp = DatePicker(get_mock_input(), get_mock_output(), name=dp_name)
		self.assertIsNotNone(dp)
		for key_name, callback in dp.keymap.iteritems():
			self.assertIsNotNone(callback)

	# Test whether it returns None when deactivating it
	def test_left_key_returns_none(self):
		dp = DatePicker(get_mock_input(), get_mock_output(), name=dp_name)
		dp.refresh = lambda *args, **kwargs: None

		# Checking at start
		def scenario():
			dp.deactivate()
			assert not dp.in_foreground

		with patch.object(dp, 'idle_loop', side_effect=scenario) as d:
			return_value = dp.activate()
		assert return_value is None

		# Chacking after moving a few cells
		def scenario():
			for i in range(3):
				dp.move_down()
				dp.move_right()
			dp.deactivate()
			assert not dp.in_foreground

		with patch.object(dp, 'idle_loop', side_effect=scenario) as d:
			return_value = dp.activate()
		assert return_value is None

if __name__ == '__main__':
	unittest.main()