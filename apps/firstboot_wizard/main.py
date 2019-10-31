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

    def do_firstboot(self):
        return # WIP code - works, but is unfinished
        file = None
        new_file = False
        for file in firstboot_file_locations:
            if os.path.exists(file):
                logger.info("Firstboot list file {} found")
                break
        else:
            logger.info("No firstboot list files found, creating one")
            for file_path in firstboot_file_locations:
                # try and touch the file
                try:
                    open(file_path, "w").close()
                    new_file = True
                except:
                    logger.exception("Can't create a firstboot list file at {}, skipping".format(file_path))
                else:
                    logger.info("Created a firstboot list file at {}".format(file_path))
                    break
            else:
                # We can't create any files!
                logger.error("Can't create a firstboot list file! Locations: {}".format(firstboot_file_locations))
                return
        firstboot_actions = cm.am.get_firstboot_actions()
        firstboot_action_names = list(firstboot_actions.keys())
        executed_action_names = []
        completed_action_names = []
        if not new_file:
          try:
            with open(file, 'r') as f:
                completed_action_names = [l.strip() for l in f.readlines() if l.strip()]
          except:
            logger.exception("Couldn't load completed actions from firstboot list file")
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
                #self.context.signal_finished()
                return
            else:
                # User confirmed that they want to go through with the firstboot wizard
                pass
