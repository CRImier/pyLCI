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

        * ``func``: callable to be run
        * ``*args``: positional arguments for the callable
        * ``**kwargs``: keyword arguments for the callable"""
    _running = False
    _finished = False
    
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.active_lock = Lock()
    
    def run(self):
        """Run the callable. Sets the ``running`` and ``finished`` attributes 
        as the function progresses. This function doesn't handle exceptions."""
        with self.active_lock:
            if self.running or self.finished:
                return
            self._running = True
        self.func(*self.args, **self.kwargs)
        with self.active_lock:
            self._running = False
            self._finished = True
        return value

    def reset(self):
        """Resets all flags, allowing the callable to be run once again.
        Will raise an Exception if the callable is still running."""
        if self.running:
            raise Exception("Runner can't be reset while still running")
        self._running = False
        self._finished = False

    @property
    def running(self):
        """Shows whether the callable is still running after it has been launched
        (assuming it has been launched)."""
        with self.active_lock:
            value = self._running
        return value

    @property
    def finished(self):
        """Shows whether the callable has finished running after it has been launched
        (assuming it has been launched)."""
        with self.active_lock:
            value = self._finished
        return value

class BackgroundRunner():
    """Background runner for callables. Once launched, it'll run in background until it's done..
    You can query on whether the runner has finished, and whether it's still running.
    
    Args:

        * ``func``: function to be run
        * ``*args``: positional arguments for the function
        * ``**kwargs``: keyword arguments for the function"""

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
        """Shows whether the callable is still running after it has been launched
        (assuming it has been launched)."""
        with self.active_lock:
            value = bool(self._running)
        return value

    @property
    def finished(self):
        """Shows whether the callable has finished running after it has been launched
        (assuming it has been launched)."""
        with self.active_lock:
            value = bool(self._finished)
        return value

    @property
    def failed(self):
        """Shows whether the callable has thrown an exception during execution
        (assuming it has been launched). The exception info will be stored in
        ``self.exc_info``."""
        with self.active_lock:
            value = bool(self._failed)
        return value

    def threaded_runner(self, print_exc=True):
        """Actually runs the callable. Sets the ``running`` and ``finished`` attributes 
        as the callable progresses. This method catches exceptions, stores 
        ``sys.exc_info`` in ``self.exc_info``, unsets ``self.running`` and 
        re-raises the exception.

        Not to be called directly!"""
        with self.active_lock:
            self._running.set(True)
        try:
            self.func(*self.args, **self.kwargs)
        except:
            self.exc_info = sys.exc_info
            if print_exc: traceback.print_exc()
            with self.active_lock:
                self._running.set(False)
                self._failed.set(True)
        else:
            with self.active_lock:
                self._running.set(False)
                self._finished.set(True)

    def run(self, daemonize=True):
        """Starts a thread that will run the callable."""
        if self.running:
            return
        self.thread = Thread(target=self.threaded_runner)
        self.thread.daemon=daemonize
        self.thread.start()

    def reset(self):
        """Resets all flags, restoring a clean state of the runner."""
        self._running.set(False)
        self._finished.set(False)
        self._failed.set(False)
        self.exc_info = None
