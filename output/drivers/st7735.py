from luma_driver import LumaScreen
from luma.lcd.device import st7735

from output.output import OutputDevice
from backlight import BacklightManager

class Screen(LumaScreen, OutputDevice):
 
  default_height = 128
  default_width = 128

  def init_display(self, rotate=0, h_offset=0, v_offset=0):
      width = self.height if rotate%2==1 else self.width
      height = self.width if rotate%2==1 else self.height
      self.device = st7735(self.serial, width=width, height=height, bgr=True, rotate=rotate, h_offset=h_offset, v_offset=v_offset)

  def enable_backlight(self, *args, **kwargs):
      BacklightManager.enable_backlight(self, *args, **kwargs)

  def disable_backlight(self, *args, **kwargs):
      BacklightManager.disable_backlight(self, *args, **kwargs)
