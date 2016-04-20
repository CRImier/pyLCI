.. _apps_scripts:

####################
Script execution app
####################

This application lets you run various pre-defined scripts and commands.

.. note:: It isn't yet capable of stopping application's execution or displaying application's output.
	
Defining applications is done in ``config.json`` file which is located in the application's directory (currently ``apps/scripts``). Its format is as follows:

.. code:: json

   [
    {"path":"./s/login.sh", #Defining a script which's located relative to application directory (``apps/scripts``)
     "name":"Hotspot login"}, #Defining a pretty name which'll be displayed by pyLCI in the application menu
    {"path":"/root/backup.sh", #Defining a script by absolute path
     "name":"Backup things",
     "args":["--everything", "--now"]}, #Giving command-line arguments to a script
    {"path":"mount", #Calling an external command available from $PATH
     "name":"'mount' with -a", 
     "args":["-a"]} #Again, command-line arguments
   ]

.. note:: #-starting comments aren't accepted in JSON and are provided solely for visual 

It also gets all the scripts in ``s/`` folder in application's directory and adds them to the script menu, if they're not available in ``config.json``.
If name is not provided, it falls back to using script's filename.
