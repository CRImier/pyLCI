.. _input_hid:

#####################
HID input driver
#####################

Sample config.json:

.. code:: json

    "input":                
       [{                   
         "driver":"hid",
         "kwargs":          
          {                 
           "name":"HID 04d9:1603"
          }                 
       }]                  


To get device names, you can just run ``python input/driver/hid.py`` while your device is connected. It will output available device names.

.. toctree::

.. automodule:: input.drivers.hid
 
.. autoclass:: InputDevice
    :members:
    :special-members:

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

