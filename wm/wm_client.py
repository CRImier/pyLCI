import Pyro4

wm = Pyro4.Proxy("PYRONAME:wcs.window_manager")

while True:
    name = raw_input("Input application name:")
    if not name.strip(" "): break
    application = wm.get_application(name)

#name = raw_input("Input window name:")

#window = application.get_window(name)

#input_interface = application.get_input_interface()
#output_interface = application.get_output_interface()

#raw_input()

application.destroy_window(window)
