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
        window = Window(name)
        self.wm.register_window(window)
        self._pyroDaemon.register(window)
        return window

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


class InputInterface():

    def __init__(self):
        pass

    def activate(self):
        pass

    def deactivate(self):
        pass


class Window():

    input_interface = InputInterface()
    output_interface = OutputInterface()

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name


@Pyro4.expose(instance_mode="single")
class WindowManager():
    applications = []
    windows = []

    _input_driver = None
    _output_driver = None

    def __init__(self, input, output):
        self._input_driver = input
        self._output_driver = output

    def get_application(self, name):
        app = Application(name, self)
        self._pyroDaemon.register(app)
        return app

    def register_application(self, app):
        #Generate UID for app number
        self.applications.append(app)
        print("Application {0} is registered".format(app.name))

    def register_window(self, window):
        print("Window {0} is registered".format(window.name))

    def destroy_window(self, window):
        print("Window {0} is destroyed".format(window.name))

    def open_window(self):
        self.plug_interface_to_driver(self._input_driver, window.input_interface)
        self.plug_interface_to_driver(self._output_driver, window.output_interface)

    def close_window(self): 
        self.unplug_interface(self._input_driver)
        self.unplug_interface(self._output_driver)
        
    def plug_interface_to_driver(self, driver, interface):
        driver.interface = interface

    def unplug_interface(self, driver):
        driver.interface = None

    def get_active_application(self):
        return self.applications[self.active_app]

    def get_active_window(self):
        return self.applications[self.active_app].window

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
        self.ns.register("wcs.window_manager", self.uri)
        self.thread.start()
        self.app.activate()
