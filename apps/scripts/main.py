menu_name = "Scripts" #App name as seen in main menu while using the system

scripts_dir = "s/"
config_filename = "config.json"
default_config = """[
 {"path":"./s/login.sh",
  "name":"Hotspot login"},
 {"path":"./s/dmesg.sh",
  "name":"Last 100 dmesg lines"},
 {"path":"/root/backup.sh",
  "name":"Backup things",
  "args":["--everything", "--now"]},
 {"path":"mount",
  "name":"'mount' with -a",
  "args":["-a"]},
 {"path":"wget",
  "name":"wget google main page",
  "args":["http://www.google.com"]}
]"""

from subprocess import check_output, CalledProcessError, STDOUT
from time import sleep
import os, sys, shlex

from helpers import read_or_create_config, local_path_gen
from ui import Menu, Printer, DialogBox, format_for_screen as ffs, PathPicker, NumpadCharInput

local_path = local_path_gen(__name__)
config_path = local_path(config_filename)
config = read_or_create_config(config_path, default_config, menu_name+" app")


def call_external(script_list, shell=False):
    if shell == True:
        script_path = script_list.split(' ')[0]
    else:
        script_path = os.path.split(script_list[0])[1]
    Printer("Calling {}".format(script_path), i, o, 1)
    try:
        output = check_output(script_list, stderr=STDOUT, shell=shell)
    except OSError as e:
        if e.errno == 2:
            Printer("File not found!", i, o, 1)
        elif e.errno == 13:
            Printer(["Permission", "denied!"], i, o, 1)
        elif e.errno == 8:
            Printer(["Unknown format,", "forgot header?"], i, o, 1)
        else:
            error_data = ["Unknown error", ""]
            error_data += ffs(repr(e), o.cols)
            Printer(error_data, i, o, 1)
        output = ""
    except CalledProcessError as e:
        Printer(["Failed with", "code {}".format(e.returncode)], i, o, 1)
        output = e.output
    else:
        Printer("Success!", i, o, 1)
    finally:
        if not output:
            return
        answer = DialogBox("yn", i, o, message="Show output?").activate()
        if answer == True:
            Printer(ffs(output, o.cols, False), i, o, 5, True)

def call_by_path():
    path = PathPicker("/", i, o).activate()
    if path is None:
        return
    args = NumpadCharInput(i, o, message="Arguments:", name="Script argument input").activate()
    if args is not None:
        path = path+" "+args
    call_external(path, shell=True)
        
def call_command():
    command = NumpadCharInput(i, o, message="Command:", name="Script command input").activate()
    if command is None:
        return
    call_external(command, shell=True)
        

def callback():
    script_menu_contents = [["Script by path", call_by_path],
                            ["Custom command", call_command]]
    scripts_in_config = []
    for script_def in config:
        script_path = script_def["path"]
        if script_path.startswith('./'):
            script_path = script_path.lstrip('.').lstrip('/')
            script_path = local_path(script_path)
            scripts_in_config.append(script_path)
        args = script_def["args"] if "args" in script_def else []
        script_name = script_def["name"] if "name" in script_def else os.path.split(script_path)[1]
        script_list = [script_path]+args
        script_menu_contents.append([script_name, lambda x=script_list: call_external(x)])
    other_scripts = os.listdir(local_path(scripts_dir))
    for script in other_scripts:
        relpath = local_path(scripts_dir, script)
        if relpath not in scripts_in_config:
            script_menu_contents.append([os.path.join(scripts_dir, script), lambda x=relpath: call_external([x])])
    Menu(script_menu_contents, i, o, "Script menu").activate()

i = None; o = None

def init_app(input, output):
    global i, o
    i = input; o = output
