.. _apps_update:

################
pyLCI update app
################

This application updates your pyLCI install by pulling the latest commits straight from pyLCI GitHub. 

.. note:: Do remember this updates only the pyLCI install currently running, effectively, doing a ``git pull`` in the current directory. So, if it's launched (it is unless you're launching it manually at the moment) from the install directory (most likely), it'll "git pull" inside the download directory (/opt/pylci by default), and vice-versa.
