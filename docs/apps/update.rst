.. _apps_update:

################
ZPUI update app
################

This application updates your ZPUI install by pulling the latest commits straight from ZPUI GitHub. 

.. note:: Do remember this updates only the ZPUI install currently running, effectively, doing a ``git pull`` in the current directory. So, if it's launched (it is unless you're launching it manually at the moment) from the install directory (most likely), it'll "git pull" inside the download directory (/opt/zpui by default), and vice-versa.
