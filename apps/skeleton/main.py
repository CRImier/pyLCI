menu_name = "App name as seen in main menu"

from subprocess import call
from ui import Menu
from time import sleep

def call_internal():
    o.display_data("Calling internal", "command")
    print("Success")
    sleep(3)

def call_external():
    o.display_data("Calling external", "command")
    call(['echo', 'Success'])
    sleep(3)

#Some globals for LCS
main_menu = None
callback = None
#Some globals for us
i = None
o = None

main_menu_contents = [
["Internal command", call_internal],
["External command", call_external],
["Exit", 'exit']
]

def init_app(input, output):
    global main_menu, callback, i, o
    i = input; o = output
    main_menu = Menu(main_menu_contents, i, o, "Skeleton app menu")
    callback = main_menu.activate

