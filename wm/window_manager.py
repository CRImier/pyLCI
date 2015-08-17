import Pyro4

from threading import Thread

import logging

logging.basicConfig(level=logging.DEBUG)

class Application():
    window = None

    def __init__(self, name, wm):
        logging.debug("Application \"{}\" initialising".format(name))
        self.wm = wm
        self._name = name
        self.wm.register_application(self)

    @property
    def name(self):
        return self._name

    @property
    def number(self):
        return self._number

    #def start(self):
    #    raise NotImplementedException

    def get_window(self, name):
        logging.debug("Application - getting window")
        self.window = Window(name)
        self._pyroDaemon.register(self.window)
        self.wm.register_window(self.window)
        return self.window

    #def open_window(self, window):
    #    raise NotImplementedException

    #def close_window(self, window):
    #    raise NotImplementedException

    def destroy_window(self, window):
        logging.debug("Application \"{}\" destroying its window".format(self.name))
        self.wm.destroy_window(window)

    #def exec_startup_triggers(self, triggers):
    #    raise NotImplementedException

    def shutdown(self):
        self.destroy_window(self.window)
        self.wm.destroy_application(self)
        logging.info("Application \"{}\" shutting down".format(self.name))


class OutputInterface():

    displayed_data = []

    def __init__(self):
        pass
    
    def activate(self):
        pass

    def deactivate(self):
        pass

    def display_data(self, *args):
        self.displayed_data = args


class InputInterface():

    keymap = {}

    def __init__(self):
        pass

    def get_available_keys(self):
        pass

    def set_callback(self, *args):
        pass

    def remove_callback(self, key_name):
        pass

    def set_keymap(self, keymap):
        self.keymap = keymap

    def replace_keymap_entries(self, keymap):
        pass

    def clear_keymap(self):
        pass

    def listen(self):
        pass

    def stop_listen(self):
        pass


class Window():

    def __init__(self, name):
        logging.debug("Window \"{}\" initialising".format(name))
        self._name = name
        self._input_interface = InputInterface()
        self._output_interface = OutputInterface()

    def init(self):
        self._pyroDaemon.register(self._input_interface)
        self._pyroDaemon.register(self._output_interface)

    @property
    def name(self):
        return self._name

    @property
    def output_interface(self):
        return self._output_interface

    @property
    def input_interface(self):
        return self._input_interface


@Pyro4.expose(instance_mode="single")
class WindowManager():
    applications = []
    windows = []

    _input_driver = None
    _output_driver = None

    active_app = None

    def __init__(self, input, output):
        self._input_driver = input
        self._output_driver = output
        self.configure_input()

    def init(self):
        """Has Pyro-specific functions which cannot be called in __init__ due to some objects not being created yet
        TODO: see if it's necessary"""
        self._pyroDaemon.register(self._output_driver)
        self._pyroDaemon.register(self._input_driver)

    def create_new_application(self, name):
        app = Application(name, self)
        self._pyroDaemon.register(app)
        logging.info("Application \"{0}\" has been created".format(app.name))
        return app

    def register_application(self, app):
        self.applications.append(app)
        app._number = len(self.applications)-1
        logging.info("Application \"{0}\" has been registered".format(app.name))

    def destroy_application(self, app):
        logging.info("Application \"{0}\" destroy initiated".format(app.name))
        self.deactivate_app(app.number)
        self.remove_application_from_apps(app)

    def remove_application_from_apps(self, app):
        logging.debug("Removing application \"{0}\" from app list".format(app.name))
        self.applications.remove(app)

    def register_window(self, window):
        window.init()
        logging.info("Window \"{0}\" has been registered".format(window.name))

    def destroy_window(self, window):
        #TODO
        logging.info('Window \"{0}\" has been destroyed'.format(window.name))

    def activate_current_window(self):
        print "Interfaces are being added"
        self.deactivate_wm_menu()
        self.plug_interface_to_driver(self._input_driver, self.get_active_window().input_interface)
        self.plug_interface_to_driver(self._output_driver, self.get_active_window().output_interface)

    def activate_app(self, number):
        self.active_app = number
        self.activate_current_window()

    def deactivate_app(self, number):
        if self.active_app == number:
            self.active_app = None
        self.deactivate_driver_interfaces()
        self.activate_wm_menu()

    def deactivate_active_app(self):
        self.deactivate_app(self.active_app)
        self.active_app = None

    def get_active_application(self):
        return self.applications[self.active_app]

    def get_active_window(self):
        return self.get_active_application().window

    def get_app_list(self):
        #app_list = []
        #for app in self.applications:
        #    app_d = {}
        #    app_d["name"] = app.name
        #    app_d["status"] = app.status
        #    app_list.append(app_d)
        #app_list.append(app)
        #return app_list
        return self.applications

    #Functions related to drivers and interfaces

    def configure_input(self):
        self._input_driver.comm_error_func = self._handle_crash

    def get_active_interfaces(self):
        window = self.get_active_window()
        return window.input_interface, window.output_interface

    def _handle_crash(self, *args):
        print "Crashed"
        self.deactivate_active_app()
        self.activate_wm_menu()
        
    def plug_interface_to_driver(self, driver, interface):
        driver._interface = interface
        driver._signal_interface_addition()

    def unplug_interface(self, driver):
        print "WM - unplugging interfaces"
        driver._interface = None
        driver._signal_interface_removal()

    def deactivate_driver_interfaces(self): 
        self.unplug_interface(self._input_driver)
        self.unplug_interface(self._output_driver)
        

class WindowManagerRunner():

    def __init__(self, input, output):
        self.input = input
        self.output = output
        self.wm = WindowManager(input, output)
        self.daemon = Pyro4.Daemon()
        self.thread = Thread(target=self.daemon.requestLoop)
        self.thread.daemon = True

    def run(self, app_object):
        self.app = app_object([], self.output, self.input, "WM menu")
        self.app.wm = self.wm
        self.ns = Pyro4.locateNS()
        self.uri = self.daemon.register(self.wm)
        self.wm.init() #The call isn't necessaey for normal operation
        self.ns.register("wcs.window_manager", self.uri)
        self.thread.start()
        self.app.init()
        self.app.activate()
