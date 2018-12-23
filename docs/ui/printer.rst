.. _ui_printer:

#####################
Printer UI element
#####################

.. code-block:: python
                      
    from ui import Printer
    Printer(["Line 1", "Line 2"], i, o, 3, skippable=True)
    Printer("Long lines will be autosplit", i, o, 1)

.. currentmodule:: ui

.. autofunction:: Printer

.. autofunction:: PrettyPrinter

.. autofunction:: GraphicsPrinter
