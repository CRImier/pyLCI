menu_name = "Shutdown&reboot"

from subprocess import call
from ui import Menu


def shutdown():
    o.clear()
    o.display_data("Shutting down")
    call(['shutdown', '-h', 'now'])

def reboot():
    o.clear()
    o.display_data("Rebooting")
    call(['reboot'])

#Some globals for LCS
main_menu = None
callback = None
#Some globals for us
i = None
o = None

main_menu_contents = [
["Shutdown", shutdown],
["Reboot", reboot],
["Exit", 'exit']
]

def init_app(input, output):
    global main_menu, callback, i, o
    i = input; o = output
    main_menu = Menu(main_menu_contents, i, o, "Shutdown menu")
    callback = main_menu.activate

