.. _input_pi_gpio:

##############################
Raspberry Pi GPIO input driver
##############################

Driver for buttons connected to GPIO. Up to 8 button are supported now.
Sample config.json:

.. code:: json

    "input":
       [{
         "driver":"pi_gpio",
         "kwargs":
          {
           "button_pins":[25, 24, 23, 18, 22, 27, 17, 4]
          }
       }]

.. toctree::

.. automodule:: input.drivers.pi_gpio
 
.. autoclass:: InputDevice
    :members:
    :special-members:
