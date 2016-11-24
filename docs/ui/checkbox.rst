.. _ui_checkbox:

#####################
Checkbox UI element
#####################

``from ui import Checkbox
contents = [
["Apples", 'apples'],
["Oranges", 'oranges'],
["Bananas", 'bananas']]
selected_fruits = Checkbox(checkbox_contents, i, o).activate()
``

.. automodule:: ui.checkbox
 
.. autoclass:: Checkbox
    :members: __init__,activate,deactivate,set_contents,move_up,move_down,flip_state,print_name,print_contents
