.. _app_mgmt:
                    
####################################
Managing and developing applications
####################################

General information
===================

* Applications are simply folders. pyLCI loads ``main.py`` file residing in that folder. It needs an ``init_app()`` function inside the main.py file. It also expects a variable called ``callback`` which is called when the application is activated by launching it from the menu.
* You can make submenus for main menu, which allows you to make it less cluttered. Submenu is just a folder which has ``__init__.py`` file in it, but doesn't have a ``main.py`` file. It can store both application folders and child submenu folders.

   .. note: To set a main menu name for your submenu, you need to add ``_menu_name = "Pretty name"`` in ``__init__.py`` file of a submenu.
   .. note: Submenus can be nested - just create another folder inside a submenu folder. However, submenu inside an application folder won't be detected.

* All application modules are loading when pyLCI loads. When choosing an application in the main menu, its global ``callback`` is called. It's usually set as the ``activate()`` method of application's main UI element, such as menu.
* You can prevent any application from loading by placing a ``do_not_load`` file (with any contents) in application's folder (for example, see skeleton application folder).

Development tips
================

* For starters, take a look at the :ref:`skeleton app <skeleton_app>`
* You can launch pyLCI in a "single application mode" using ``main.py -a apps/app_folder_path``. There'll be no main menu constructed, and exiting the application exits pyLCI.
* You should not set input callbacks or output to screen while your application is not the one active. It'll cause screen contents set from another application to be overwritten, which is bad for using pyLCI.
Make sure your application is the one currently active before outputting things.
