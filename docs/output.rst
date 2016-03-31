##############
Output devices
##############

Currently pyLCI uses HD44780-compatible screens as output devices. Minimum screen size is 16x2.
Available output drivers:

.. toctree::
   :maxdepth: 1

   output/mcp23008.rst
   output/pcf8574.rst
   output/pifacecad.rst
   output/pi_gpio.rst

=============
Screen object
=============

The ``o`` variable you have supplied by ``main.py`` ``load_app()`` in your applications is a ``Screen`` instance. It provides you with a set of functions available to HD44780 displays.
Most of drivers just provide low-level functions for ``HD44780`` object, which, in turn, provides ``Screen`` object users with high-level functions described below:

.. automodule:: output.drivers.hd44780
.. autoclass:: HD44780
    :members:
    :special-members:

=====================
Glue logic functions:
=====================

.. warning:: Not for user interaction, are called by ``main.py``, which is pyLCI main script.

.. autofunction:: output.output.init


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
