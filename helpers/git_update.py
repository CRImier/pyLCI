"""This module contains various helpers that help maintain the ZPUI's 
"update from git" capability and solve various problems that might happen 
while trying to integrate this capability into existing apps."""
from threading import Lock
import importlib
#pip is a heavy import, so will make the ZPUI startup significantly longer
#Thus, it's postponed
pip = None 

installing = Lock()

def install_from_pip(package):
    """This is a helper to install a package from PyPi (using ``pip``) if it's
    not yet available on the system. Will not run simultaneously when called from
    multiple threads, instead, will wait for already running instance to finish."""
    global pip
    with installing:
        #If pip hasn't yet been imported, let's import it
        if not pip:
            pip = importlib.import_module("pip")
        pip.main(['install', package])
