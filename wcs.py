import threading 

import Pyro4 
import Pyro4.util 

#Pyro4.config.REQUIRE_EXPOSE = True #Would be necessary but breaks input drivers. Proceed with caution.

wm = Pyro4.Proxy("PYRONAME:wcs.window_manager") 

thread = None

_daemon = Pyro4.Daemon() 

def register_object(object):
    _daemon.register(object) 

def start_daemon_thread():
    global thread
    thread = threading.Thread(target=_daemon.requestLoop) 
    thread.daemon = True
    thread.start()

def run(function, atexit):
    try:
        function()
    except:
        raise
    finally:
        if atexit:
            atexit()
