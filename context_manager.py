from input.input import InputProxy

import logging
from functools import wraps

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def call_in_context(func, cm, context_alias):
    @wraps(func)
    def wrapper(*args, **kwargs):
        previous_context = cm.get_current_context()
        cm.switch_to_context(context_alias)
        try:
            func(*args, **kwargs)
        except:
            raise
        finally:
            cm.switch_to_context(previous_context)
    return wrapper


class ContextManager(object):

    current_context = None
    initial_contexts = ["main"]

    def __init__(self):
        self.context_objects = {}
        self.context_activation_callbacks = {}

    def init_io(self, input_processor, screen):
        self.input_processor = input_processor
        self.screen = screen
        self.init_contexts()
        self.set_context_callbacks()

    def init_contexts(self):
        for context_alias in self.initial_contexts:
            self.create_context(context_alias)

    def list_contexts(self):
        return self.context_objects.keys()

    def get_current_context(self):
        return self.current_context

    def switch_to_context(self, context_alias):
        logger.info("Switching to context {}".format(context_alias))
        self.current_context = context_alias
        proxy_i, proxy_o = self.get_io_for_context(context_alias)
        self.input_processor.detach_current_proxy()
        self.input_processor.attach_proxy(proxy_i)
        #self.o.detach_current_proxy()
        #self.o.attach_proxy(proxy_i)
        for callback in self.context_activation_callbacks[context_alias]:
            callback()

    def request_context_activation(self, context_alias):
        logger.info("Received a request to activate the {} context".format(context_alias))
        if context_alias in ["notification", "phone"]:
            self.switch_to_context(context_alias)
            return True
        else:
            logger.info("Request to switch context accepted")
            return False
        
    def set_context_activation_callback(self, context_alias, callback):
        self.context_activation_callbacks[context_alias].append(callback)

    def create_context(self, context_alias):
        logger.info("Creating context {}".format(context_alias))
        input_proxy = InputProxy(context_alias)
        output_proxy = self.screen
        self.context_objects[context_alias] = (input_proxy, output_proxy)
        self.input_processor.register_proxy(input_proxy, context_alias)
        self.context_activation_callbacks[context_alias] = []

    def get_io_for_context(self, context_alias):
        if context_alias not in self.context_objects:
            self.create_context(context_alias)
        return self.context_objects[context_alias]
    
    def set_context_callbacks(self):
        pass
        #app_i = self.context_objects["app"][0]
        #app_i.set_nonmaskable_callback("KEY_ANSWER", lambda: self.switch_to_context("phone"))
        #app_i.set_nonmaskable_callback("KEY_PROG2", lambda: self.switch_to_context("clock+lock"))
