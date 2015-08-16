import Pyro4

from threading import Thread

class Application():
    window = None

    def __init__(self, name, wm):
        self.wm = wm
        self._name = name
        self.wm.register_application(self)

    @property
    def name(self):
        return self._name

    def start(self):
        pass

    def get_window(self, name):
        self.window = Window(name)
        self._pyroDaemon.register(self.window)
        self.wm.register_window(self.window)
        return self.window

    def open_window(self, window):
        pass

    def close_window(self, window):
        pass

    def destroy_window(self, window):
        self.wm.destroy_window(window)

    def exec_startup_triggers(self, triggers):
        pass


class OutputInterface():

    def __init__(self):
        pass
    
    def activate(self):
        pass

    def deactivate(self):
        pass

    def display_data(self, *args):
        pass


class InputInterface():

    keymap = {}
    callback_object = None

    def __init__(self):
        pass

    def get_available_keys(self):
        pass

    def set_callback_object(self, object):
        pass

    def set_callback(self, key_name, callback):
        pass

    def remove_callback(self, key_name):
        pass

    def set_keymap(self, keymap):
        pass

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
        input.comm_error_func = self.handle_crash

    def init(self):
        self._pyroDaemon.register(self._output_driver)
        self._pyroDaemon.register(self._input_driver)

    def get_application(self, name):
        app = Application(name, self)
        self._pyroDaemon.register(app)
        return app

    def register_application(self, app):
        #Generate UID for app number
        self.applications.append(app)
        self.active_app = len(self.applications)-1
        print("Application {0} is registered".format(app.name))

    def register_window(self, window):
        window.init()
        print("Window {0} is registered".format(window.name))

    def destroy_window(self, window):
        print("Window {0} is destroyed".format(window.name))

    @Pyro4.oneway
    def activate_current_window(self):
        self.deactivate_wm_menu()
        self.plug_interface_to_driver(self._input_driver, self.get_active_window().input_interface)
        self.plug_interface_to_driver(self._output_driver, self.get_active_window().output_interface)

    def deactivate_window(self): 
        self.unplug_interface(self._input_driver)
        self.unplug_interface(self._output_driver)
        
    def plug_interface_to_driver(self, driver, interface):
        driver._interface = interface
        driver._signal_interface_addition()

    def unplug_interface(self, driver):
        driver.interface = None
        driver._signal_interface_removal()

    def activate_app(self, number):
        self.active_app = number
        window = self.applications[self.active_app].window
        self.activate_window(window)

    def deactivate_active_app(self):
        self.active_app = None
        self.deactivate_window()

    def handle_crash(self, *args):
        self.deactivate_active_app()
        self.activate_wm_menu()

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
        self.wm.init()
        self.ns.register("wcs.window_manager", self.uri)
        self.thread.start()
        self.app.init()
        self.app.activate()
