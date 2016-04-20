################
Output subsystem
################

Currently pyLCI uses HD44780-compatible screens as output devices. Minimum screen size is 16x2, 20x4 screens are tested and working.
Available output drivers:

   * :ref:`output_pcf8574`
   * :ref:`output_pifacecad`
   * :ref:`output_adafruit`
   * :ref:`output_pi_gpio`
   * :ref:`output_mcp23008`

=============
Screen object
=============

The ``o`` variable you have supplied by ``main.py`` ``load_app()`` in your applications is a ``Screen`` instance. It provides you with a set of functions available to HD44780 displays.
Most of drivers just provide low-level functions for ``HD44780`` object, which, in turn, provides ``Screen`` object users with high-level functions described below:

.. automodule:: output.drivers.hd44780
.. autoclass:: HD44780
    :members:
    :special-members:

.. rubric:: Glue logic functions

.. warning:: Not for user interaction, are called by ``main.py``, which is pyLCI launcher.

.. autofunction:: output.output.init

.. toctree::
   :maxdepth: 2

   output/mcp23008.rst
   output/pcf8574.rst
   output/pifacecad.rst
   output/adafruit.rst
   output/pi_gpio.rst

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
