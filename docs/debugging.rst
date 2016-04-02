#########################
Debugging issues
#########################

=====================
HD44780 screen issues
=====================

Currently pyLCI uses HD44780-compatible screens as output devices. Minimum screen size is 16x2. There are some known issues which may arise when using those.

.. rubric:: Basic debugging steps:

* See the logs (launch system manually or use ``journalctl``).
* In case of I2C connection, check your I2C backpack's address with i2cdetect.
* Launch driver manually to display the test sequence. Go to the directory you installed pyLCI from and launch the output driver directly like "python output/drivers/your_driver.py". You might need to adjust variables in ``if __name__ == "__main__":`` section.
* Check your connections.

.. rubric:: Screen displaying garbage

* Check your connections. Seriously. Like, once again. Some breakouts might use same ICs but have different pinouts, even *slightly* different pinouts.
* Try and tie D0-D3 lines to GND. Those lines floating freely may cause instabilities. 
* You can try to tie the R/W line to GND, too. It's even necessary in some cases, like Pi GPIO driver.
* Put a ~100pF capacitor between GND and EN.

.. rubric:: Screen characters being shifted incorrectly

* Try to set ``"autoscroll":True`` in ``config.json`` in output description.

.. rubric:: Only half of the screen is used

* Make sure you didn't set ``"autoscroll":True`` in ``config.json`` in output description.

.. rubric:: Nothing on the screen

* Is first row of blocks shown? If not, regulate the contrast with a potentiometer. You can also try to tie the contrast pin to GND.
* Does screen receive 5V (not 3.3V) as VCC? Unless it's a screen that's capable of doing 3.3V (must be stated in screen's description), that's a no-go.
* Is the driver even correct? See the config.json and documentation for the driver you're using. 

============
Input issues
============



* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
