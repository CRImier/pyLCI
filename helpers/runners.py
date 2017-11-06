from threading import Lock, Thread, Event
import traceback
import sys

class BooleanEvent():
    def __init__(self):
       self._e = Event()

    def __bool__(self):
        return self._e.isSet()

    __nonzero__ = __bool__

    def set(self, state):
        if state:
            self._e.set()
        else:
            self._e.clear()

class Oneshot():
    """Oneshot runner for callables. Each instance of Oneshot will only run once, unless reset.
    You can query on whether the runner has finished, and whether it's still running.
    
    Args:

        *``func``: function to be run
        *``*args``: positional arguments for the function
        *``**kwargs``: keyword arguments for the function"""
    _running = False
    _finished = False
    
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.active_lock = Lock()
    
    def run(self):
        if self.running or self.finished:
            return
        self.active_lock.acquire()
        self._running = True
        self.active_lock.release()

        self.func(*self.args, **self.kwargs)

        self.active_lock.acquire()
        self._running = False
        self._finished = True
        self.active_lock.release()

    def reset(self):
        if self.running:
            raise Exception("Runner can't be reset while still running")
        self._finished = False

    @property
    def running(self):
        self.active_lock.acquire()
        value = self._running
        self.active_lock.release()
        return value

    @property
    def finished(self):
        self.active_lock.acquire()
        value = self._finished
        self.active_lock.release()
        return value

class BackgroundRunner():
    """Background runner for callables. Once launched, it'll run in background until it's done..
    You can query on whether the runner has finished, and whether it's still running.
    
    Args:

        *``func``: function to be run
        *``*args``: positional arguments for the function
        *``**kwargs``: keyword arguments for the function"""

    exc_info = None

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.active_lock = Lock()
        self._running = BooleanEvent()
        self._finished = BooleanEvent()
        self._failed = BooleanEvent()

    @property
    def running(self):
        self.active_lock.acquire()
        value = bool(self._running)
        self.active_lock.release()
        return value

    @property
    def finished(self):
        self.active_lock.acquire()
        value = bool(self._finished)
        self.active_lock.release()
        return value

    @property
    def failed(self):
        self.active_lock.acquire()
        value = bool(self._failed)
        self.active_lock.release()
        return value

    def threaded_runner(self, print_exc=True):
        self.active_lock.acquire()
        self._running.set(True)
        self.active_lock.release()
        try:
            self.func(*self.args, **self.kwargs)
        except:
            self.exc_info = sys.exc_info
            if print_exc: traceback.print_exc()
            print("Runner failed!")
            self.active_lock.acquire()
            self._running.set(False)
            self._failed.set(True)
            self.active_lock.release()
        else:
            self.active_lock.acquire()
            self._running.set(False)
            self._finished.set(True)
            self.active_lock.release()

    def run(self, daemonize=True):
        if self.running:
            return
        self.thread = Thread(target=self.threaded_runner)
        self.thread.daemon=daemonize
        self.thread.start()

    def reset(self):
        self._running.set(False)
        self._finished.set(False)
        self._failed.set(False)
        self.exc_info = None
