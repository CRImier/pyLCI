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

.. automodule:: ui
 
.. autoclass:: Menu
    :show-inheritance:
    :members: __init__,activate,deactivate,set_contents,print_name,print_contents,pointer,in_background,in_foreground
    
.. autoclass:: MenuExitException
    :show-inheritance:

