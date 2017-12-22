menu_name = "MOCP control"

from subprocess import call
from ui import Menu, Printer, DialogBox

callback = None
i = None
o = None

#MOCP commands
def mocp_command(*command, **options):
    try:
        return call(['mocp'] + list(command))
    except:
        #We shouldn't print anything to the screen if called from a non-maskable callback
        silent = options.get("silent", False)
        if not silent:
            Printer(["Oops", "Is mocp there?"], i, o, 1)

def mocp_toggle_play():
    mocp_command("-G")

def mocp_next(silent=False):
    mocp_command("-f", silent=silent)

def mocp_prev(silent=False):
    mocp_command("-r", silent=silent)

def option_switch_dialog(option):
    answer = DialogBox([["On", 'o'], ["Off", 'u'], ["Toggle", "t"]], i, o, message=option.capitalize()+":", name="MOCP {} option control dialog".format(option)).activate()
    if answer: mocp_switch_option(answer, option)

shuffle_dialog = lambda: option_switch_dialog("shuffle")
repeat_dialog = lambda: option_switch_dialog("repeat")
autonext_dialog = lambda: option_switch_dialog("autonext")

def mocp_switch_option(switch_type, option):
    mocp_command("-{}".format(switch_type), option)

main_menu_contents = [ 
["Toggle play/pause", mocp_toggle_play],
["Next song", mocp_next],
["Previous song", mocp_prev],
["Shuffle", shuffle_dialog],
["Repeat", repeat_dialog],
["Autonext", autonext_dialog]
]

def init_app(input, output):
    global main_menu, callback, i, o
    i = input; o = output
    #i.set_nonmaskable_callback("KEY_PROG1", lambda: mocp_next(silent=True) )
    #i.set_nonmaskable_callback("KEY_CAMERA", lambda: mocp_prev(silent=True) )
    main_menu = Menu(main_menu_contents, i, o, "MOCP menu")
    callback = main_menu.activate

