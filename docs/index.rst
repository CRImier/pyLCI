Welcome to ZPUI documentation!
=================================

ZPUI stands for ZeroPhone UI, it's the official user interface for ZeroPhone (installed on ZeroPhone official SD card images). It allows you to interact with your ZeroPhone, using the 1.3" OLED and the 30-button numpad.

ZPUI is based on pyLCI, a general-purpose UI for embedded devices. However, unlike pyLCI, 
ZPUI is tailored for the ZeroPhone hardware, namely, the 1.3" monochrome OLED 
and 30-key numpad (though it still retains input&output drivers from pyLCI), and 
it also ships with ZeroPhone-specific applications.

Guides:
=======

* :doc:`Installing and updating ZPUI <setup>`
* :ref:`Installing ZPUI emulator <emulator>`
* :doc:`Hacking on UI <hacking_ui>`

References:
===========

* :doc:`UI elements <ui>`
* :doc:`Helper functions <helpers>`
* :doc:`Input system <input>`
* :doc:`Output system <output>`


:doc:`Development plans <plans>`

:doc:`Contact us <contact>`

:doc:`Working on documentation <docs_development>`


.. toctree::
   :maxdepth: 1
   :hidden:

   setup.rst
   ui.rst
   helpers.rst
   hacking_ui.rst
   hardware.rst
   debugging.rst
   input.rst
   output.rst
   apps.rst
   app_mgmt.rst
   plans.rst
   docs_development.rst
   contact.rst
