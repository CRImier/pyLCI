menu_name = "WiFi repair"

from time import sleep

from ui import LoadingBar, PrettyPrinter as Printer, TextReader
from helpers import setup_logger

from libs import dkms_debug

logger = setup_logger(__name__, "debug")

try:
    import kmodpy
except:
    kmodpy = None
    logger.exception("Kmodpy module not found!")

i = None
o = None

dkms_fail_text = """DKMS fail - driver not installed! Run:
   apt install --reinstall esp8089-dkms
to fix the problem (sorry, we can't do that automatically yet)."""

def init_app(input, output):
    global i, o
    i = input
    o = output

def callback():
    problem_found = False
    problem_fixed = False
    logger.debug("App launched")
    li = LoadingBar(i, o, message="Fixing WiFi")
    li.run_in_background()
    sleep(1) # Showing the message a little bit
    # TODO: check Zero/ZeroW
    logger.debug("Checking DKMS")
    li.message = "Checking DKMS"
    info = dkms_debug.get_dkms_status_info()
    logger.debug(info)
    if not dkms_debug.dkms_driver_is_installed("esp8089", dkms_info=info):
        problem_found = True
        logger.debug("DKMS driver not found!")
        li.stop()
        TextReader(dkms_fail_text, i, o, h_scroll=False).activate()
    logger.debug("DKMS driver was found")
    if not problem_found and kmodpy:
        li.message = "Checking module"
        logger.debug("Checking module")
        sleep(1)
        modules = dict(kmodpy.kmod.Kmod().list())
        logger.debug(modules)
        if "esp8089" not in modules:
            logger.debug("Module not loaded")
            li.message = "Loading module"
            try:
                kmodpy.kmod.Kmod().modprobe("esp8089")
            except kmodpy.kmod.KmodError as e:
                logger.exception("Error while loading module!")
                message = e.message
                logger.error(message)
                if message == 'Module already loaded':
                    logger.error("That's weird!")
                elif message == "Could not modprobe 'esp8089'":
                    problem_found = True
                    logger.info("ESP not accessible?")
                else:
                    logger.error("Unknown error!")
            except:
                problem_found = True
                logger.exception("Yet-unknown module loading error")
                Printer("Unknown loading error!", i, o)
            else:
                problem_found = True
                problem_fixed = True
                Printer("Loaded module!", i, o)
        else:
            logger.debug("Module loaded")
    else:
        logger.debug("Module load check - problem not found yet and kmodpy not available")
    # Next things:
    # Check dmesg
    # Check config.txt, edit if necessary
    li.stop()
    if problem_found:
        if problem_fixed:
            Printer("Fixed some problems!", i, o)
        else:
            Printer("Couldn't fix problems!", i, o)
    else:
        Printer("No problems found!", i, o)
