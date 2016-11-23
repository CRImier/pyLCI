.. _app_mgmt:
                    
####################################
Managing and developing applications
####################################

General information
===================

* Applications are simply folders which are made importable by Python by adding an ``__init__.py`` file. pyLCI loads ``main.py`` file residing in that folder. It needs an ``init_app()`` function inside the main.py file. It also expects a variable called ``callback`` which is called when the application is activated by launching it from the menu, and a variable named ``menu_name`` which contains a name that'll be shown in the main menu.
* You can combine UI elements in many different ways, including making nested menus, which makes apps less cluttered. 
* pyLCI main menu can have submenus. Submenu is just a folder which has ``__init__.py`` file in it, but doesn't have a ``main.py`` file. It can store both application folders and child submenu folders.

  * To set a main menu name for your submenu, you need to add ``_menu_name = "Pretty name"`` in ``__init__.py`` file of a submenu.
  * Submenus can be nested - just create another folder inside a submenu folder. However, submenu inside an application folder won't be detected.

* All application modules are loading when pyLCI loads. When choosing an application in the main menu/submenu, its global ``callback`` is called. It's usually set as the ``activate()`` method of application's main UI element, such as a menu.
* You can prevent any application from autoloading (but still have an option to load it manually) by placing a ``do_not_load`` file (with any contents) in application's folder (for example, see skeleton application folder).

Development tips
================

* For starters, take a look at the :ref:`skeleton app <skeleton_app>`
* You can launch pyLCI in a "single application mode" using ``main.py -a apps/app_folder_path``. There'll be no main menu constructed, and exiting the application exits pyLCI.
* You should not set input callbacks or output to screen while your application is not the one active. It'll cause screen contents set from another application to be overwritten, which is bad user experience. Make sure your application is the one currently active before outputting things and setting callbacks.
