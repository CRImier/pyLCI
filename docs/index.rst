Welcome to ZPUI documentation!
=================================

ZPUI stands for ZeroPhone UI, it's the official user interface for ZeroPhone (installed on ZeroPhone official SD card images). It allows you to interact with your ZeroPhone, using the 1.3" OLED and the 30-button numpad.

ZPUI is based on pyLCI, a general-purpose UI for embedded devices. However, unlike pyLCI, 
ZPUI is tailored for the ZeroPhone hardware, namely, the 1.3" monochrome OLED 
and 30-key numpad (though it still retains input&output drivers from pyLCI), and 
it also ships with ZeroPhone-specific applications.

Guides:
=================================

* :doc:`Hacking on UI <hacking_ui>`
* :doc:`Debugging issues <debugging>`
* :doc:`Managing and developing applications <app_mgmt>`

ZPUI core consists of 5 parts:

#. :doc:`Input system <input>`
#. :doc:`Output system <output>`
#. :doc:`UI elements <ui>`
#. :doc:`Applications <apps>`
#. Glue logic (mostly main.py launcher)

:doc:`Development plans <plans>`

:doc:`Working on documentation <docs_development>`

.. toctree::
   :maxdepth: 1
   :hidden:

   hardware.rst
   setup.rst
   debugging.rst
   hacking_ui.rst
   input.rst
   output.rst
   ui.rst
   apps.rst
   app_mgmt.rst
   helpers.rst
   plans.rst
   docs_development.rst
