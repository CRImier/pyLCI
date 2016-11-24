.. _ui_number_input:

#########################
Numeric input UI elements
#########################

``from ui import IntegerAdjustInput
start_from = 0
number = IntegerAdjustInput(start_from, i, o).activate()
if number is None: #Input cancelled
    return
#process the number
``

.. automodule:: ui.number_input

.. autoclass:: IntegerAdjustInput
    :members: __init__,activate,increment,decrement,reset,select_number,deactivate,print_number,print_name
