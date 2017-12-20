###############
Input subsystem
###############

These are the devices that receive key commands from some external source and route them to your applications. 
At the input system core, there's ``InputListener``. It receives key events from drivers you use and routes them to currently active application.

Available input drivers:

   * :ref:`input_hid`
   * :ref:`input_pcf8574`
   * :ref:`input_pifacecad`
   * :ref:`input_adafruit`
   * :ref:`input_pi_gpio`

=============
InputListener
=============

The ``i`` variable you have supplied by ``main.py`` ``load_app()`` in your applications is an ``InputListener`` instance. It's operating on key names, such as "KEY_ENTER" or "KEY_UP". You can assign callback once a keypress with a matching keyname is received, which is as simple as ``i.set_callback(key_name, callback)``.
You can also set a dictionary of ``"keyname":callback_function`` mappings, this would be called a ``keymap``.


.. automodule:: input.input
 
.. autoclass:: InputListener
    :members:
    :special-members:

.. note::

   In v1.0 architecture, there's a single ``InputListener`` instance shared among all applications, so when you set some callbacks for your application and then exit it or execute your application's menu element, there's a very good chance your callbacks won't be there anymore once you return. 
   You won't need to think about it unless you're setting ``InputListener`` yourself - mostly it's taken care of by UI objects, which set the keymaps themselves themselves (for example, ``Menu`` UI element sets the callbacks each time a menu is activated and each time a menu element callback execution is finished (because a ``Menu`` can't be sure whatever got called by the callback didn't set some of callbacks some other way, say, the element's callback was activating a nested menu.)
   

If you do set callbacks/keymap yourself (very useful for making your own UI elements, or for applications needing custom keybindings), it's important to remember that you need to stop ``InputListener`` before and start it again afterwards, since the changes do not take place until that's done. For example, this is how you would set your own callback:
   
.. code-block:: python
   
   i.stop_listen()
   i.clear_keymap() #Useful because there might be callbacks left from whatever your function was called by
   #... Set your callbacks
   i.set_callback("KEY_ENTER", my_function)
   i.listen()

.. rubric:: Glue logic functions

.. warning:: Not for user interaction, are called by ``main.py``, which is ZPUI launcher.

.. autofunction:: init

========
Drivers:
========

.. toctree::
   :maxdepth: 2

   input/hid.rst
   input/pcf8574.rst
   input/pifacecad.rst
   input/adafruit.rst
   input/pi_gpio.rst
