import os
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
        if not is_emulator:
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
        if not is_new_file:
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
                for action_fullname, action in sorted_actions.items():
                    if action.depends:
                        if any([d in failed_actions for d in action.depends]):
                            logger.error("Not executing action {} because some of its dependencies ({}) are among failed dependencies: {}".format(action_fullname, action.depends, failed_actions))
                            continue
                    action_provider, action_name = get_prov_and_name(action_fullname)
                    if action.will_context_switch:
                        self.context.request_switch(action_provider, start_thread=False)
                    try:
                        action.func()
                    except:
                        logger.exception("Action {} failed to execute!".format(action_fullname))
                        failed_actions.append(action_name)
                    self.context.request_switch()
