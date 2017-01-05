#############################
Installing and updating pyLCI
#############################

.. code-block:: bash

    git clone https://github.com/CRImier/pyLCI
    cd pyLCI/
    ./setup.sh #Install main dependencies and create a install directory
    ./config.sh #Install dependencies for your input&output devices 
    nano config.json #Describe your input&outputdevices (if you have a supported shield, previous step will edit this for you)
    sudo python main.py #Start the system to test your configuration - do screen and buttons work OK?
    #Once configured:
    ./update.sh #Transfer the working system to your install directory

.. note:: 
   **Behind the scenes:**
   
   When you run ``./setup.sh``, pyLCI is copied to ``/opt/pylci``, this is done to make autorun code easier and allow experimentation while making it harder to lock you out of the system if pyLCI is your main control interface. ``/opt/pylci`` will be referred to as "install directory", while the directory you cloned the repository to will be referred to as "download directory". ``./update.sh``, when run from download directory, will transfer the changes from the download directory (and GitHub) to the install directory.

Setup
=====

``setup.sh`` is the first script to be run after installation. It checks if you have python and python-pip installed and installs them if they aren't (using apt-get), then creates the install directory, copies all the files to it and installs a ``systemd`` unit file for system to run at boot. Perfect for Raspbian and Debian Jessie, TODO: add support for other systems.
   
.. note:: The system typically runs as root, and therefore is to be run as sudo/root user. Curious about the reasons? It's :doc:`explained in the FAQ <faq_contact>`.

Installing dependencies for hardware
====================================

``config.sh`` is the script that installs all the necessary packages and python libraries, depending on which hardware you're using. It will also set proper ``config.json`` contents if you're using a shield which has a pyLCI driver.

Configuring input and output devices
====================================

``config.json`` is the file currently responsible for input and output hardware module configuration. It's JSON, so if you launch the system manually and see ``JSONError`` exceptions in the output, you know you have misspelled something. 

.. note:: Generally, you won't need to edit ``config.json`` if you're using any shields recognised by ``config.sh``  because the configuration will be done automatically.

Its format is as follows: 

.. code:: json

   {
     "input":
     [{
       "driver":"driver_filename",
       "args":[ "value1", "value2", "value3"...]
     }],
   "output":
     [{
       "driver":"driver_filename",
       "kwargs":{ "key":"value", "key2":"value2"}
     }]
   }

Documentation for :doc:`input <input>` and :doc:`output <output>` drivers have sample ``config.json`` for each driver. ``"args"`` and ``"kwargs"`` get passed directly to drivers' ``__init__`` method, so you can read the driver documentation/files to see if there are any options you could tweak.

Systemctl commands
==================

* ``systemctl start pylci.service``
* ``systemctl stop pylci.service``


.. note:: 
   This document refers to two pyLCI directories. First is "download directory", this is the directory which has been created by running ``git clone`` command. Second is "install directory", which is where pyLCI has been copied over by the ``setup.sh`` script.
 
   Directory separation is good for being able to experiment with configuration options without breaking the current install, as well as for developing applications for the system while not cluttering your install version.


Launching the system manually
=============================

For testing configuration or development, you will want to launch the system directly so that you'll see system exception logs and will be able to stop it with a simple Ctrl^C. In that case, just run the system like ``python main.py`` from your download/install directory. 

.. tip:: If system refuses to shut down (happens due to input subsystem threads not finishing sometimes), feel free to find its PID using ``ps ax|grep "python main.py"`` and do a ``kill -KILL $PID`` on it.

After you're done configuring/developing on the system, you can use ``update.sh`` to transfer your changes to the install directory.

Updating
========

``update.sh`` is for updating your pyLCI install, pulling new commits from GitHub and copying all the new files from download directory to the install directory. This is useful to make your installed system up-to-date if there have been new commits or if you made some changes and want to transfer them to pyLCI install directory. 

.. note:: ``update.sh`` automatically pulls all the GitHub commits - just comment the corresponding line out if you don't want it. It also runs ``systemctl start pylci.service``.
