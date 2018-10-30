menu_name = "WiFi repair"

from time import sleep

from ui import LoadingBar, PrettyPrinter as Printer, TextReader, Listbox, DialogBox
from helpers import setup_logger

from libs import dmesg, dkms_debug
from libs.rpi import vcgencmd, rpiinfo

import sdio_debug

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

otp_fail_text = """Your Pi has an OTP fault!
Visit bit.ly/pi_bad_otp for more info.
Press LEFT to pick your hardware."""

def get_hw_version(li):
    if rpiinfo.is_pi_zero():
       if rpiinfo.is_pi_zero_w():
           return "zerow"
       else:
           return "zero"
    else:
        li.pause()
        if vcgencmd.otp_problem_detected(vcgencmd.otp_dump()):
            TextReader(otp_fail_text, i, o, h_scroll=False).activate()
        else:
            Printer("Hardware detect failed! Pick your hardware:", i, o, 5)
        lc = [["Pi Zero", "zero"], ["Pi Zero W", "zerow"], ["Other", "other"]]
        choice = Listbox(lc, i, o, name="WiFi repair - hw revision picker").activate()
        li.resume()
        return choice

def check_esp8089_dkms(li):
    logger.debug("Checking DKMS")
    li.message = "Checking DKMS"
    info = dkms_debug.get_dkms_status_info()
    logger.debug(info)
    if not dkms_debug.dkms_driver_is_installed("esp8089", dkms_info=info):
        logger.debug("DKMS driver not found!")
        li.pause()
        TextReader(dkms_fail_text, i, o, h_scroll=False).activate()
        li.resume()
        return True
    logger.debug("DKMS driver was found!")
    return False

def check_esp8089_module(li):
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
            message = e.message.strip()
            logger.error(message)
            if message == 'Module already loaded':
                logger.error("That's weird, ESP8089 module detect fail but modprobe says it's already loaded!")
            elif message == "Could not modprobe 'esp8089'":
                logger.info("ESP not accessible?")
            else:
                logger.error("Unknown error!")
        except:
            logger.exception("Yet-unknown ESP8089 module loading error")
            li.pause()
            Printer("Unknown ESP8089 module loading error!", i, o)
            li.resume()
        else:
            li.pause()
            Printer("Loaded ESP8089 module!", i, o)
            li.resume()
            return True, True
    else:
        logger.debug("ESP8089 module already loaded")
    return False, False

def check_dmesg(li):
    li.message = "Checking dmesg"
    sleep(0.5)
    logger.info("Parsing dmesg output")
    dmesg_msgs = dmesg.get_dmesg()
    if sdio_debug.check_lowlevel_mmc_errors(dmesg_msgs):
        li.pause()
        logger.exception("Low-level MMC errors!")
        Printer("Low-level MMC errors!", i, o)
        li.resume()
        # problem found
        return True
    # problem not found
    return False

def init_app(input, output):
    global i, o
    i = input
    o = output

def callback():
    problem_found = False
    problem_fixed = False
    logger.debug("App launched")
    li = LoadingBar(i, o, message="Detecting hardware")
    li.run_in_background()
    sleep(1) # Showing the message a little bit
    hw_version = get_hw_version(li)
    if not hw_version:
        return False # User pressed LEFT in Listbox
    # DKMS check
    # if hardware is undetected, do we need to check it?
    # ask the user.
    hw_wrong_but_check_esp = False
    if hw_version == "other":
        hw_wrong_but_check_esp = DialogBox("yn", i, o, message="Using ESP8266?").activate()
    # This deals with ESP8266 problems
    if hw_version == "zero" or hw_wrong_but_check_esp:
        #check dkms module
        problem_found = check_esp8089_dkms(li)
        #check esp8089 module
        if not problem_found:
            if kmodpy:
                problem_found, problem_fixed = check_esp8089_module(li)
            else:
                logger.debug("kmodpy not available, not checking the esp8089 module")
        # Check dmesg
        if not problem_found:
            problem_found = check_dmesg(li)
    # Next things:
    # Check config.txt (for both Pi Zero and Pi Zero W), edit if necessary
    li.stop()
    if problem_found:
        if problem_fixed:
            Printer("Fixed some problems!", i, o)
        else:
            Printer("Couldn't fix problems!", i, o)
    else:
        Printer("No problems found!", i, o)