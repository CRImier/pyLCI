#############################
Installing and updating pyLCI
#############################

.. note:: 
   This document refers to two pyLCI directories. First is "download directory", this is the directory which has been created by running ``git clone`` command. Second is "install directory", which is where pyLCI has been copied over by the ``setup.sh`` script.
 
   Directory separation is good for being able to experiment with configuration options without breaking the current install, as well as for developing applications for the system.


Installation:

Git
===

``git clone https://github.com/CRImier/WCS``

Setup
=====

``setup.sh`` is the first script to be run after installation. It checks if you have python and python-pip installed and installs them if they aren't (currently, using apt-get), then creates an install directory, copies all the files to it and installs a ``systemd`` unit file for system to run at boot. Perfect for Raspbian and Debian Jessie, TODO: add support for other systems.

Installing dependencies for hardware
====================================

``config.sh`` is the script that installs all the necessary packages and python libraries, depending on which hardware you're using. 

Configuring input and output devices
====================================

``config.json`` is the file currently responsible for input and output hardware module configuration. It's JSON, so if you launch the system manually and see ``JSONError`` exceptions in the output, you know you have misspelled something. 

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

Documentation for :doc:`input <input>` and :doc:`output <output>` drivers have sample ``config.json`` for each driver. ``"args"`` and ``"kwargs"`` get passed directly to drivers' ``__init__`` method, so you can refer to that to see if there are additional attributes available for your application.

Systemctl commands
==================

* ``systemctl start pylci.service``
* ``systemctl stop pylci.service``


Launching the system manually
=============================

For testing configuration or development, you will want to launch the system directly so that you'll see system exception logs and will be able to stop it with a simple Ctrl^C. In that case, just run the system like ``python main.py`` from your download/install directory. 

.. tip:: If system refuses to shut down (happens due to input subsystem threads not finishing sometimes), feel free to find its PID using ``ps ax|grep "python main.py"`` and do a ``kill -KILL $PID`` on it.

After you're done configuring/developing on the system, you can use ``update.sh``:

Updating
========

``update.sh`` is for updating your pyLCI install, pulling new commits from GitHub and copying all the new files from download directory to the install directory. This is useful to make your installed system up-to-date if there have been new commits or if you made some changes and want to transfer them to pyLCI install directory. 

.. note:: ``update.sh`` automatically pulls all the GitHub commits - just comment the corresponding line out if you don't want it. Also, it runs ``systemctl start pylci.service``.


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



