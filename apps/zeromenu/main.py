menu_name = "ZeroMenu"

import os
from datetime import datetime
from threading import Event

from ui import Menu, PrettyPrinter, Checkbox
from helpers import read_or_create_config, local_path_gen, save_config_gen

i = None
o = None
context = None
zeromenu = None

screenshot_folder = "screenshots"

default_config = '{"ordering":[], "excluded_actions":[]}'
config_filename = "config.json"

local_path = local_path_gen(__name__)
config = read_or_create_config(local_path(config_filename), default_config, menu_name+" app")
save_config = save_config_gen(local_path(config_filename))

def take_screenshot():
    image = context.get_previous_context_image()
    if image != None:
        timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
        filename = "screenshot_{}.png".format(timestamp)
        path = os.path.join(screenshot_folder, filename)
        image.save(path, "PNG")
        PrettyPrinter("Screenshot saved to {}".format(path), i, o)

def set_context(received_context):
    global context
    context = received_context
    context.request_global_keymap({"KEY_PROG2":context.request_switch})
    context.set_target(zeromenu.activate)
    context.register_action("screenshot", take_screenshot, "Take screenshot", description="Takes a screenshot from previous app")

def set_ordering():
    pass

def manage_contents():
    global config
    cc = []
    for action in context.get_actions():
        menu_name_cb = action["menu_name_cb"]
        menu_name = menu_name_cb() if callable(menu_name_cb) else menu_name_cb
        name = action["full_name"]
        is_excluded = action["full_name"] not in config["excluded_actions"]
        cc.append([menu_name, name, is_excluded])
    choice = Checkbox(cc, i, o, default_state=False, name="ZeroMenu contents checkbox").activate()
    if choice:
        for action in choice:
            state = choice[action]
            if state == False and action not in config["excluded_actions"]:
                config["excluded_actions"].append(action)
            elif state == True and action in config["excluded_actions"]:
                config["excluded_actions"].remove(action)
        save_config(config)

def settings_menu():
    mc = [["Manage contents", manage_contents]]
    #      ["Set ordering", set_ordering]]
    Menu(mc, i, o, name="ZeroMenu settings menu").activate()

def init_app(input, output):
    global i, o, zeromenu
    i = input; o = output
    def get_contents():
        mc = []
        for action in context.get_actions():
            if action["full_name"] not in config["excluded_actions"]:
                menu_name_cb = action["menu_name_cb"]
                menu_name = menu_name_cb() if callable(menu_name_cb) else menu_name_cb
                entry = [menu_name, action["cb"]]
                if action["aux_cb"]:
                    entry.append(action["aux_cb"])
                mc.append(entry)
        mc.append(["ZM settings", settings_menu])
        return mc
    zeromenu = Menu([], i, o, name="ZeroMenu main menu", contents_hook=get_contents)

