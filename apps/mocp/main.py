menu_name = "MOCP control"

from subprocess import call
from ui.menu import Menu

#Some globals for LCS
main_menu = None
callback = None
#Some globals for us
i = None
o = None

#MOCP commands
def mocp_command(*command):
    try:
        return call(['mocp'] + list(command))
    except:
        o.display_data("Oops", "Is mocp installed?")

def mocp_toggle_play():
    mocp_command("-G")

def mocp_next():
    mocp_command("-f")

def mocp_prev():
    mocp_command("-r")

main_menu_contents = [ 
["Toggle play/pause", mocp_toggle_play],
["Next song", mocp_next],
["Previous song", mocp_prev],
["Exit", 'exit']
]

def init_app(input, output):
    global main_menu, callback, i, o
    i = input; o = output
    main_menu = Menu(main_menu_contents, o, i, "MOCP menu")
    callback = main_menu.activate

