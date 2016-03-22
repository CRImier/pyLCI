

menu_name = "Shutdown&reboot"

from subprocess import call
from menu.menu import Menu


def shutdown():
    o.display_data("Shutting down")
    call(['shutdown', '-h', 'now'])

def reboot():
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
    main_menu = Menu(main_menu_contents, o, i, "Shutdown menu")
    callback = main_menu.activate

