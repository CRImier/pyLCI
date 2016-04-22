menu_name = "Update"

from subprocess import check_output, CalledProcessError

from ui import Printer

def update():
    Printer("Updating...", i, o, 1)
    try:
        print(check_output(["git", "pull"]))
    except OSError as e:
        if e.errno == 2:
            Printer("git not found!", i, o, 1)
        else:
            Printer("Unknown error!", i, o, 1)
    except CalledProcessError as e:
        if e.returncode == 1:
            Printer(["Can't connect", "to GitHub!"], i, o, 1)
        else:
            Printer(["Failed with", "code {}".format(e.returncode)], i, o, 1)
    else:
        Printer("Success!", i, o, 1)

callback = update
i = None #Input device
o = None #Output device

def init_app(input, output):
    global i, o
    i = input; o = output