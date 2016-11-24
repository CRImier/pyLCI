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

.. automodule:: ui.menu
 
.. autoclass:: Menu
    :members: __init__,activate,deactivate,set_contents,move_up,move_down,select_element,print_name,print_contents,generate_keymap

.. autoclass:: MenuExitException

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

