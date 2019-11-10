import os

from apps import ZeroApp
from helpers import is_emulator, setup_logger
from ui import DialogBox

from __main__ import cm

logger = setup_logger(__name__, "info")


firstboot_file_locations = ["zpui_firstboot.list", "/tmp/zpui_firstboot.list"]
if not is_emulator:
    firstboot_file_locations = ["/boot/zpui_firstboot.list"]+firstboot_file_locations

class FirstbootWizard(ZeroApp):
    def set_context(self, c):
        self.context = c
        #self.context.set_target(self.do_firstboot)
        self.context.threaded = False

    def execute_after_contexts(self):
        self.do_firstboot()

    def get_firstboot_file(self):
        """ Returns ``(filename, is_new_file)``, ``(None, False)`` on failure """
        file = None
        for file in firstboot_file_locations:
            if os.path.exists(file):
                logger.info("Firstboot list file {} found")
                return (file, False)
        else:
            logger.info("No firstboot list files found, creating one")
            for file_path in firstboot_file_locations:
                # try and touch the file
                try:
                    open(file_path, "w").close()
                except:
                    logger.exception("Can't create a firstboot list file at {}, skipping".format(file_path))
                else:
                    logger.info("Created a firstboot list file at {}".format(file_path))
                    return (file, True)
            else:
                # We can't create any files!
                logger.error("Can't create any of the firstboot list files! Locations: {}".format(firstboot_file_locations))
                return (None, False)

    def get_completed_actions_from_file(self, file):
        try:
            with open(file, 'r') as f:
                return [l.strip() for l in f.readlines() if l.strip()]
        except:
            logger.exception("Couldn't load completed actions from firstboot list file")
            return []

    def do_firstboot(self):
        firstboot_actions = cm.am.get_firstboot_actions()
        firstboot_action_names = list(firstboot_actions.keys())
        file, is_new_file = self.get_firstboot_file()
        if file is None:
            logger.error("Can't read/create a firstboot file, no sense for the firstboot application to continue")
            return
        completed_action_names = []
        if not new_file:
            completed_action_names = self.get_completed_actions_from_file(file)
        non_completed_action_names = [n for n in firstboot_action_names if n not in completed_action_names]
        if non_completed_action_names:
            if not completed_action_names: # Not the first boot - some actions have been completed before
                message = "Let's go through first boot setup!"
            else:
                message = "New setup actions for your ZP found!"
            result = self.context.request_exclusive()
            if not result:
                logger.error("Can't get an exclusive context switch, exiting")
            choice = DialogBox('yn', self.i, self.o, message=message, name="Firstboot wizard setup menu").activate()
            if not choice:
                self.context.rescind_exclusive()
                return
            else:
                # User confirmed that they want to go through with the firstboot wizard
                pass
