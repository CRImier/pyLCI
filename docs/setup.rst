#############################
Installing and updating pyLCI
#############################

There are 3 scripts you can use for updating your pyLCI install.

1. ``setup.sh`` is the first one you run. It checks if you have python and python-pip installed and installs them if they aren't (currently, using apt-get), then  makes a directory in opt/ to host the system, then copies all the files over and installs a systemd unit file for system to run at boot. Perfect for Raspbian and Debian Jessie, TODO: enable other systems.

2. ``config.sh`` is the configuration script. Currently, it installs all the necessary packages and python libraries, depending on which hardware you're using. 

3. ``update.sh`` is for updating your pyLCS install, pulling new commits from GitHub and copying the files over.

config.json
===========

This file is currently responsible for input and output hardware module configuration. It's JSON, so if you launch the system manually and see ``JSONError`` exceptions in the output, you know you have misspelled something. 

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

Documentation for :doc:`input<input>` and output drivers have sample ``config.json`` for each driver. ``"args"`` and ``"kwargs"`` get passed directly to drivers' ``__init__`` method, so you can refer to that to see if there are additional attributes available for your application.

As you can see, ``config.json`` allows to specify multiple input and output devices (though it's not implemented yet). It also has room for future expansion in case it's necessary, for example, to make a "globals" section to control system's parameters.

.. toctree::
   :maxdepth: 1


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



