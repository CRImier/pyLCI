import os
import json
from copy import copy
from collections import OrderedDict

from apps import ZeroApp
from helpers import is_emulator, setup_logger, flatten
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
                logger.info("Firstboot list file {} found".format(file))
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
        actions = []
        try:
            with open(file, 'r') as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
                for line in lines:
                  try:
                    action_dict = json.loads(line)
                  except ValueError:
                    actions.append(line)
                  else:
                    actions.append(action_dict)
            return actions
        except:
            logger.exception("Couldn't load completed actions from firstboot list file")
            return []

    def do_firstboot(self):
        firstboot_actions = cm.am.get_firstboot_actions()
        # Skipping actions that shouldn't be run in an emulator
        if is_emulator:
            firstboot_action_names = [name for name, action in firstboot_actions.items() if not action.not_on_emulator]
        else:
            firstboot_action_names = list(firstboot_actions.keys())
        firstboot_file, is_new_file = self.get_firstboot_file()
        if firstboot_file is None:
            logger.error("Can't read/create a firstboot file, no sense for the firstboot application to continue")
            return
        completed_action_names = []
        failed_action_names = []
        skipped_action_names = []
        if not is_new_file:
            completed_action_names = []
            completed_actions = self.get_completed_actions_from_file(firstboot_file)
            for action in completed_actions:
                if isinstance(action, basestring):
                    completed_action_names.append(action)
                elif isinstance(action, dict):
                    action_name = action["action"]
                    action_result = action["status"]
                    if action_result == "success":
                        # If action has been recorded as failed/skipped before and later was marked as successful
                        # we don't need to count the fails/skips in
                        while action_name in skipped_action_names: skipped_action_names.remove(action_name)
                        while action_name in failed_action_names: failed_action_names.remove(action_name)
                        completed_action_names.append(action_name)
                    elif action_result == "fail":
                        # if action failed before, it being skipped before/after is irrelevant
                        failed_action_names.append(action_name)
                        while action_name in skipped_action_names: skipped_action_names.remove(action_name)
                    elif action_result == "skip":
                        if action_name not in failed_action_names:
                            skipped_action_names.append(action_name)
        non_completed_action_names = [n for n in firstboot_action_names if n not in completed_action_names and n not in skipped_action_names]
        # print(non_completed_action_names, skipped_action_names, failed_action_names, completed_action_names)
        if non_completed_action_names:
            if is_new_file or (not completed_action_names and not skipped_action_names and not failed_action_names):
                # first boot, no info whatsoever yet
                message = "Let's go through first boot setup!"
            elif not completed_action_names and not failed_action_names: # Not the first boot - some actions have been completed before
                message = "New setup actions for your ZP found!"
            elif failed_action_names and set(completed_action_names) == set(failed_action_names): # Some actions have not been successfully completed
                message = "Want to retry failed first boot actions?"
            else: # ought to make a truth table, I guess
                message = "New setup actions for your ZP found!"
            if not self.context.request_exclusive():
                logger.error("Can't get an exclusive context switch, exiting")
                return
            choice = DialogBox('yn', self.i, self.o, message=message, name="Firstboot wizard setup menu").activate()
            if not choice:
                self.context.rescind_exclusive()
                return
            else:
                # User confirmed that they want to go through with the firstboot wizard
                # Let's sort the actions and resolve their dependencies
                # For that, we need some storage variables.
                # Here, we store actions by their fullname, sorted in order to
                # resolve the dependency problems
                sorted_actions = OrderedDict()
                # Here, we store lists of actions that depend on some other action,
                # sorted by the execution order (after resolving the dependencies)
                action_dependants = {}
                # Here, we store action fullnames (provider+separator+name)
                # by their short names (just action name, no 'provider' appended)
                # because short names are used in dependencies.
                action_fullname_by_name = {}
                def get_prov_and_name(action_fullname):
                    return action_fullname.split(cm.am.action_name_delimiter, 1)
                # First, creating a lookup table for looking up dependencies
                for action_fullname in firstboot_action_names:
                    _, action_name = get_prov_and_name(action_fullname)
                    action_fullname_by_name[action_name] = action_fullname
                # Then, compiling the list of actions that depend on other action
                for action_fullname in non_completed_action_names:
                    _, action_name = get_prov_and_name(action_fullname)
                    action = firstboot_actions[action_fullname]
                    if action.depends:
                        has_unresolved_dependencies = False
                        for dependency in action.depends:
                            dep_fullname = action_fullname_by_name.get(dependency, None)
                            if dep_fullname is None:
                                logger.error("Dependency {} for action {} is not found!".format(dep_fullname, action_name))
                                continue
                            if dep_fullname in non_completed_action_names:
                                has_unresolved_dependencies = True
                                # dependency hasn't been completed yet
                                if dep_fullname in action_dependants:
                                    action_dependants[dep_fullname].append(action_fullname)
                                else:
                                    action_dependants[dep_fullname] = [action_fullname]
                            else:
                                logger.info("Dependency {} (for action {}) is already completed!".format(dep_fullname, action_name))
                        if not has_unresolved_dependencies:
                            # No non-completed dependencies have been found
                            # so, we can just add the action to the list
                            sorted_actions[action_fullname] = action
                    else:
                        # Action doesn't depend on anything, just adding it to the list
                        sorted_actions[action_fullname] = action
                # This code untangles an arbitrarily long chain of dependencies
                # except, well, circular dependencies
                if action_dependants:
                    original_dependants = copy(action_dependants)
                    logger.info("Resolving dependencies: {}".format(action_dependants))
                    while action_dependants:
                        all_dependency_actions = action_dependants.keys()
                        all_dependent_actions = flatten(action_dependants.values())
                        independent_dependencies = [n for n in all_dependency_actions if n not in all_dependent_actions]
                        if not independent_dependencies:
                            logger.error("No independent dependencies found while resolving dependencies: {} (original: {})!".format(action_dependants, original_dependants))
                            return
                        for action_fullname in independent_dependencies:
                            if action_fullname not in sorted_actions:
                                sorted_actions[action_fullname] = firstboot_actions[action_fullname]
                            action_dependants.pop(action_fullname)
                    # The while() has run its course and the dependencies have been linearized
                    all_dependent_actions = flatten(original_dependants.values())
                    all_unadded_dependent_actions = [n for n in all_dependent_actions \
                      if n not in sorted_actions]
                    for action_fullname in all_unadded_dependent_actions:
                        sorted_actions[action_fullname] = firstboot_actions[action_fullname]
                    logger.info("Dependencies resolved!")
                # Now, executing actions one-by-one
                failed_actions = []
                log_completed_action_has_failed = False
                for action_fullname, action in sorted_actions.items():
                    if action.depends:
                        if any([d in failed_actions for d in action.depends]):
                            logger.error("Not executing action {} because some of its dependencies ({}) are among failed dependencies: {}".format(action_fullname, action.depends, failed_actions))
                            continue
                    action_provider, action_name = get_prov_and_name(action_fullname)
                    if action.will_context_switch:
                        self.context.request_switch(action_provider, start_thread=False)
                    try:
                        result = action.func()
                    except:
                        logger.exception("Action {} failed to execute!".format(action_fullname))
                        failed_actions.append(action_name)
                    else:
                        if result is False: # Action failed internally
                            failed_actions.append(action_name)
                        status = {False:"fail", True:"success", None:"skip"}.get(result, "success")
                        action_dict = {"action":action_fullname, "status":status}
                        action_result = json.dumps(action_dict)
                        try:
                            with open(firstboot_file, 'a') as f:
                                f.write(action_result+'\n')
                        except:
                            # Avoid cluttering the logs - logger.exception writes the entire traceback into logs
                            # while logger.error just writes the error message
                            if not log_completed_action_has_failed:
                                logger.exception("Can't write action {} into firstboot logfile {}!".format(action_fullname, firstboot_file))
                                log_completed_action_has_failed = True
                            else:
                                logger.error("Can't write action {} into firstboot logfile {}!".format(action_fullname, firstboot_file))
                    self.context.request_switch()
