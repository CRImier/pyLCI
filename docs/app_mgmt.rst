.. _app_mgmt:
                    
####################################
Managing and developing applications
####################################

General information
===================

* Applications are simply folders inside apps/ folder. pyLCI loads ``main.py`` file residing in that folder.
* All application modules are loading when pyLCI loads. When choosing that application in the main menu, its global ``callback`` is called. Typically this is ``activate()`` method of application's main UI element, such as menu.
* You can prevent any application from loading by placing a ``do_not_load`` file with any contents in application's folder (for example, see skeleton application).

Development tips
================

* For starters, take a look at the :ref:`skeleton app <skeleton_app>`
* You can launch pyLCI with a single application using ``main.py -a app_folder_name``. There'll be no pyLCI main menu constructed, exiting the application exits pyLCI.
* You should not set input callbacks or output to screen while your application is not the one active.
