.. _ui_printer:

#####################
Printer UI element
#####################

.. code-block:: python
                      
    from ui import Printer
    Printer(["Line 1", "Line 2"], i, o, 3, exitable=True)
    Printer("Long lines will be autosplit", i, o, 1)

.. automodule:: ui.printer

.. autofunction:: Printer

.. autofunction:: PrettyPrinter

.. autofunction:: GraphicsPrinter
