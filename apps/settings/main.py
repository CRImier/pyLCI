import os
import signal
from subprocess import check_output, CalledProcessError

from ui import Menu, Printer, DialogBox

menu_name = "Settings"


def update():
    Printer("Updating...", i, o, 1)
    try:
        output = check_output(["bash", "update.sh"])
        Printer("Updated ZPUI", i, o, 1)
        needs_restart = DialogBox('yn', i, o, message="Restart the UI?").activate()
        if needs_restart:
            os.kill(os.getpid(), signal.SIGTERM)
    except OSError as e:
        if e.errno == 2:
            Printer("git not found!", i, o, 1)
        else:
            Printer("Unknown OSError!", i, o, 1)
    except CalledProcessError as e:
        if e.returncode == 1:
            #  Need to check output - can also be "Conflicting local changes" and similar
            Printer(["Can't connect", "to GitHub?"], i, o, 1)

        if e.returncode == 126:
            Printer(["ZPUI already", "up-to-date"], i, o, 1)
        else:
            Printer(["Failed with", "code {}".format(e.returncode)], i, o, 1)


def settings():
    c = [["Update ZPUI", update]]
    Menu(c, i, o, "Global settings menu").activate()


callback = settings
i = None  # Input device
o = None  # Output device


def init_app(input, output):
    global i, o
    i = input; o = output
