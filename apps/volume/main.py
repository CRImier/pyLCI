menu_name = "Volume control"

mixer_name="PCM"
volume_up_value = "400+"
volume_down_value = "400-"

from subprocess import call
from ui import Menu

#amixer commands
def amixer_command(*command):
    return call(['amixer'] + list(command))

def plus_volume():
    return amixer_command("-c", "0", "--", "sset", mixer_name, volume_up_value)

def minus_volume():
    return amixer_command("-c", "0", "--", "sset", mixer_name, volume_down_value)

def toggle_mute():
    return amixer_command("-c", "0", "--", "sset", mixer_name, "toggle")



#Some globals for LCS
main_menu = None
callback = None
#Some globals for the application
i = None
o = None

main_menu_contents = [ 
["Increase volume", plus_volume],
["Decrease volume", minus_volume],
["Toggle mute", toggle_mute],
["Exit", 'exit']
]

def init_app(input, output):
    global main_menu, callback, i, o
    i = input; o = output
    main_menu = Menu(main_menu_contents, i, o, "Volume menu")
    callback = main_menu.activate

