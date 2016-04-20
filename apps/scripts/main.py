menu_name = "Scripts" #App name as seen in main menu while using the system

from subprocess import check_output, CalledProcessError
from time import sleep
import os

base_dir = "apps/scripts"
scripts_dir = "s/"

from helpers.config_parse import read_config
from ui import Menu, Printer

def call_external(script_list):
    Printer("Calling {}".format(os.path.split(script_list[0])[1]), i, o, 1)
    try:
        check_output(script_list)
    except OSError as e:
        if e.errno == 2:
            Printer("File not found!", i, o, 1)
        elif e.errno == 13:
            Printer(["Permission", "denied!"], i, o, 1)
        else:
            Printer("Unknown error!", i, o, 1)
    except CalledProcessError as e:
        Printer(["Failed with", "code {}".format(e.returncode)], i, o, 1)
    else:
        Printer("Success!", i, o, 1)
        
def show_menu():
    script_menu_contents = []
    config = read_config(os.path.join(base_dir, "config.json"))
    scripts_in_config = []
    for script_def in config:
        script_path = script_def["path"]
        if script_path.startswith('./'):
            script_path = script_path.lstrip('.').lstrip('/')
            script_path = os.path.join(base_dir, script_path)
            scripts_in_config.append(script_path)
        args = script_def["args"] if "args" in script_def else []
        script_name = script_def["name"] if "name" in script_def else os.path.split(script_path)[1]
        script_list = [script_path]+args
        script_menu_contents.append([script_name, lambda x=script_list: call_external(x)])
    other_scripts = os.listdir(os.path.join(base_dir, scripts_dir))
    for script in other_scripts:
        relpath = os.path.join(base_dir, scripts_dir, script)
        if relpath not in scripts_in_config:
            script_menu_contents.append([os.path.join(scripts_dir, script), lambda x=relpath: call_external([x])])
    Menu(script_menu_contents, i, o, "Script menu").activate()

callback = show_menu
i = None #Input device
o = None #Output device

def init_app(input, output):
    global i, o
    i = input; o = output
