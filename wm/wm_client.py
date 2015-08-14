import Pyro4
import Pyro4.util

wm = Pyro4.Proxy("PYRONAME:wcs.window_manager")

#name = raw_input("Input application name:")
application = wm.get_application("App 1")

#name = raw_input("Input window name:")

window = application.get_window("Window 1")

#input_interface = application.get_input_interface()
output_interface = window.output_interface

try:
    wm.activate_current_window()
except Exception:
    print("Pyro traceback:")
    print("".join(Pyro4.util.getPyroTraceback()))


user_input = "String"
while user_input:
    user_input = raw_input("Enter data to display:")
    args = []
    for i in range((len(user_input)/16)+1):
         row = user_input[i*16:][:16]
         print(row)
         args.append(row)
    output_interface.display_data(*args)


application.destroy_window(window)
