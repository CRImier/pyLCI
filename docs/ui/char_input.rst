.. _ui_char_input:

###########################
Character input UI elements
###########################

``from ui import CharArrowKeysInput
password = CharArrowKeysInput(i, o, message="Password:", name="My password dialog").activate()
if password is None: #UI element exited 
    return False #Cancelling
#processing the input you received...``

.. automodule:: ui.char_input

.. autoclass:: CharArrowKeysInput
    :members: __init__,activate,move_up,move_down,move_left,move_right,accept_value,deactivate,print_value,print_name
