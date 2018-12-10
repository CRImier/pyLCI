menu_name = "Hardware setup"

import os

from ui import Menu, PrettyPrinter as Printer, DialogBox, LoadingIndicator, PathPicker #, UniversalInput, Refresher, IntegerAdjustInput
from helpers import setup_logger, read_or_create_config, local_path_gen, write_config, save_config_gen

import smbus

from mtkdownload import MTKDownloadProcess

local_path = local_path_gen(__name__)
logger = setup_logger(__name__, "warning")
default_config = '{"mtkdownload_path":"mtkdownload"}'
config_path = local_path("config.json")
config = read_or_create_config(config_path, default_config, menu_name+" app")
save_config = save_config_gen(config_path)

i = None
o = None

def change_settings():
    menu_contents = [
    ["Set mtkdownload path", set_mtkdownload_path]]
    Menu(menu_contents, i, o, "ZP hardware setup settings menu").activate()

def set_mtkdownload_path():
    default_path = config["mtkdownload_path"] if os.path.isabs(config["mtkdownload_path"]) else "/"
    path = PathPicker(default_path, i, o, name="Hardware setup app mtkdownload path picker").activate()
    if path:
        config["mtkdownload_path"] = path
        save_config(config)

def flash_image_ui():
    if not MTKDownloadProcess(None, None, path=config["mtkdownload_path"]).mtkdownload_is_available():
        Printer("mtkdownload not found!", i, o, 5)
        choice = DialogBox("yn", i, o, name="Hardware setup app mtkdownload path confirmation", message="Set mtkdownload path?").activate()
        if choice:
            if set_mtkdownload_path():
                callback()
            else:
                return
    pass

def init_app(input, output):
    global main_menu, callback, i, o
    i = input; o = output

def callback():
    main_menu_contents = [
    ["Flash GSM modem", flash_image_ui],
    ["Settings", change_settings]]
    Menu(main_menu_contents, i, o, "ZP hardware setup menu").activate()
