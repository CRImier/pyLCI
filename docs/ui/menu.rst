.. _ui_menu:

#####################
Menu UI element
#####################

.. code-block:: python
                      
    from ui import Menu
    ... 
    menu_contents = [
    ["Do this", do_this],
    ["Do this with 20", lambda: do_this(x=20)],
    ["Do nothing"],
    ["My submenu", submenu.activate]
    ]
    Menu(menu_contents, i, o, "My menu").activate()

``Menu`` always returns ``None``, so you don't need to check its return value.

.. automodule:: ui
 
.. autoclass:: Menu
    :show-inheritance:
    :members: __init__,activate,deactivate,set_contents
    
.. autoclass:: MenuExitException
    :show-inheritance:

