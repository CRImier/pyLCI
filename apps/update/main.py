menu_name = "Update pyLCI"

from subprocess import check_output, CalledProcessError

from ui import Printer

def update():
    Printer("Updating...", i, o, 1)
    try:
        output = check_output(["git", "pull"])
        if "Already up-to-date." in output:
            Printer("All up-to-date", i, o, 1)
        else:
            Printer("Updated pyLCI", i, o, 1)
    except OSError as e:
        if e.errno == 2:
            Printer("git not found!", i, o, 1)
        else:
            Printer("Unknown OSError!", i, o, 1)
    except CalledProcessError as e:
        if e.returncode == 1:
            Printer(["Can't connect", "to GitHub?"], i, o, 1) #Need to check output - can also be "Conflicting local changes" and similar
        else:
            Printer(["Failed with", "code {}".format(e.returncode)], i, o, 1)

callback = update
i = None #Input device
o = None #Output device

def init_app(input, output):
    global i, o
    i = input; o = output
