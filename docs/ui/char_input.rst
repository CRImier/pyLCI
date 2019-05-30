.. _ui_char_input:

###########################
Character input UI elements
###########################

.. code-block:: python

    from ui import CharArrowKeysInput
    password = CharArrowKeysInput(i, o, message="Password:", name="My password dialog").activate()
    if password is None: #UI element exited 
        return False #Cancelling
    #processing the input you received...

.. currentmodule:: ui

.. autoclass:: CharArrowKeysInput
    :members: __init__,activate,deactivate
