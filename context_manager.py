from input.input import InputProxy

import logging
from functools import wraps
from threading import Thread

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def context_target_wrapper(func, cm, context_alias, previous_context):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except:
            raise
        finally:
            #Only switch to the previous context if this context is the one active
            if cm.get_current_context() == context_alias:
                cm.switch_to_context(previous_context)
    return wrapper


class ContextManager(object):

    current_context = None
    initial_contexts = ["main"]

    def __init__(self):
        self.context_objects = {}
        self.context_threads = {}
        self.context_targets = {}

    def init_io(self, input_processor, screen):
        self.input_processor = input_processor
        self.screen = screen
        self.init_contexts()

    def init_contexts(self):
        for context_alias in self.initial_contexts:
            self.create_context(context_alias)

    def list_contexts(self):
        return self.context_objects.keys()

    def get_current_context(self):
        return self.current_context

    def register_thread_target(self, target, context_alias):
        logger.debug("Registering a thread target for the {} context".format(context_alias))
        self.context_targets[context_alias] = target

    def create_thread_for_context(self, context_alias, previous_context):
        logger.info("Creating a new thread for the {} context".format(context_alias))
        wrapped_target = context_target_wrapper(self.context_targets[context_alias], self, context_alias, previous_context)
        t = Thread(target=wrapped_target)
        t.daemon = True
        if context_alias in self.context_threads:
            del self.context_threads[context_alias]
        self.context_threads[context_alias] = t

    def activate_thread_for_context(self, context_alias, previous_context = "main"):
        if context_alias not in self.context_targets:
            raise ValueError("Can't switch to {} context - no context target available!".format(context_alias))
        if context_alias in self.context_threads and self.context_threads[context_alias].isAlive():
            #A thread already exists and is active, doing nothing
            return
        #Thread either doesn't exist yet or was created but already stopped running
        self.create_thread_for_context(context_alias, previous_context)
        self.context_threads[context_alias].start()

    def switch_to_context(self, context_alias):
        logger.info("Switching to {} context".format(context_alias))
        previous_context = self.current_context
        self.current_context = context_alias
        if context_alias is not "main":
            self.activate_thread_for_context(context_alias, previous_context)
        self.activate_context_io(context_alias)
        logger.info("Switched to {} context!".format(context_alias))

    def activate_context_io(self, context_alias):
        """
        This method activates input and output objects associated with a context.
        """
        logger.debug("Activating IO for {} context".format(context_alias))
        proxy_i, proxy_o = self.get_io_for_context(context_alias)
        self.input_processor.detach_current_proxy()
        self.input_processor.attach_proxy(proxy_i)
        if self.screen.current_image:
            self.screen.display_image(self.screen.current_image)
        #self.screen.detach_current_proxy()
        #self.screen.attach_proxy(proxy_o)

    def create_context(self, context_alias):
        logger.info("Creating {} context".format(context_alias))
        input_proxy = InputProxy(context_alias)
        output_proxy = self.screen
        self.set_context_callbacks(input_proxy)
        self.input_processor.register_proxy(input_proxy, context_alias)
        self.context_objects[context_alias] = (input_proxy, output_proxy)

    def get_io_for_context(self, context_alias):
        if context_alias not in self.context_objects:
            self.create_context(context_alias)
        return self.context_objects[context_alias]
    
    def set_context_callbacks(self, proxy_i):
        proxy_i.set_nonmaskable_callback("KEY_PROG2", lambda: self.switch_to_context("apps/zeromenu"))
