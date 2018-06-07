import os
import signal
from subprocess import check_output, STDOUT, CalledProcessError
from time import sleep

try:
    import httplib
except:
    import http.client as httplib

from ui import Menu, PrettyPrinter, DialogBox, ProgressBar, Listbox
from helpers.logger import setup_logger

import logging_ui

menu_name = "Settings"
logger = setup_logger(__name__, "info")


class GitInterface(object):

    @classmethod
    def git_available(cls):
        try:
            cls.command("--help")
        except OSError:
            return False
        return True

    @staticmethod
    def command(command):
        commandline = "git {}".format(command)
        logger.debug("Executing: {}".format(commandline))
        return check_output(commandline, shell=True, stderr=STDOUT)

    @classmethod
    def get_head_for_branch(cls, branch):
        output = cls.command("rev-parse {}".format(branch)).strip()
        return output

    @classmethod
    def get_current_branch(cls):
        return cls.get_head_for_branch("--abbrev-ref HEAD").strip()

    @classmethod
    def checkout(cls, reference):
        return cls.command("checkout {}".format(reference))

    @classmethod
    def pull(cls, source = "origin", branch = "master", opts="--no-edit"):
        try:
            return cls.command("pull {2} {0} {1}".format(source, branch, opts))
        except CalledProcessError as e:
            lines = iter(e.output.split('\n'))
            logger.debug("Parsing output")
            marker1 = "following untracked working tree files would be overwritten by merge"
            marker2 = "local changes to the following files would be overwritten by merge"
            for line in lines:
                logger.debug(repr(line))
                if marker1 in line or marker2 in line:
                    logger.info("Found interfering files!")
                    line = next(lines)
                    while line.startswith('\t'):
                        line = line.strip()
                        if not line.endswith('/'):
                            try:
                                logger.info("Removing interfering file: {}".format(line))
                                os.remove(line)
                            except OSError:
                                logger.warning("Couldn't remove an interfering file {} while pulling!".format(line))
                        line = next(lines)
            return cls.command("pull {2} {0} {1}".format(source, branch, opts))


class UpdateUnnecessary(Exception):
    pass


class GenericUpdater(object):
    steps = []
    progressbar_messages = {}
    failed_messages = {}

    def run_step(self, step_name):
        logger.info("Running update step: '{}'".format(step_name))
        getattr(self, "do_" + step_name)()
        logger.debug("Update step '{}' completed!".format(step_name))

    def revert_step(self, step_name):
        if hasattr(self, "revert_" + step_name):
            logger.info("Reverting update step: '{}'".format(step_name))
            getattr(self, "revert_" + step_name)()
            logger.debug("Update step '{}' reverted!".format(step_name))
        else:
            logger.debug("Can't revert step {} - no reverter available.".format(step_name))

    def update(self):
        logger.info("Starting update process")
        pb = ProgressBar(i, o, message="Updating ZPUI")
        pb.run_in_background()
        progress_per_step = 100 / len(self.steps)

        completed_steps = []
        try:
            for step in self.steps:
                pb.set_message(self.progressbar_messages.get(step, "Loading..."))
                sleep(0.5)  # The user needs some time to read the message
                self.run_step(step)
                completed_steps.append(step)
                pb.progress += progress_per_step
        except UpdateUnnecessary:
            logger.info("Update is unnecessary!")
            pb.stop()
            PrettyPrinter("ZPUI already up-to-date!", i, o, 2)
        except:
            # Name of the failed step is contained in `step` variable
            failed_step = step
            logger.exception("Failed on step {}".format(failed_step))
            failed_message = self.failed_messages.get(failed_step, "Failed on step '{}'".format(failed_step))
            pb.pause()
            PrettyPrinter(failed_message, i, o, 2)
            pb.set_message("Reverting update")
            pb.resume()
            try:
                logger.info("Reverting the failed step: {}".format(failed_step))
                self.revert_step(failed_step)
            except:
                logger.exception("Can't revert failed step {}".format(failed_step))
                pb.pause()
                PrettyPrinter("Can't revert failed step '{}'".format(step), i, o, 2)
                pb.resume()
            logger.info("Reverting the previous steps")
            for step in completed_steps:
                try:
                    self.revert_step(step)
                except:
                    logger.exception("Failed to revert step {}".format(failed_step))
                    pb.pause()
                    PrettyPrinter("Failed to revert step '{}'".format(step), i, o, 2)
                    pb.resume()
                pb.progress -= progress_per_step
            sleep(1) # Needed here so that 1) the progressbar goes to 0 2) run_in_background launches the thread before the final stop() call
            #TODO: add a way to pause the Refresher
            pb.stop()
            logger.info("Update failed")
            PrettyPrinter("Update failed, try again later?", i, o, 3)
        else:
            logger.info("Update successful!")
            sleep(0.5)  # showing the completed progressbar
            pb.stop()
            PrettyPrinter("Update successful!", i, o, 3)
            self.suggest_restart()

    def suggest_restart(self):
        needs_restart = DialogBox('yn', i, o, message="Restart ZPUI?").activate()
        if needs_restart:
            os.kill(os.getpid(), signal.SIGTERM)


class GitUpdater(GenericUpdater):
    branch = "master"

    steps = ["check_connection", "check_git", "check_revisions", "pull", "install_requirements", "pretest_migrations", "tests"]
    progressbar_messages = {
        "check_connection": "Connection check",
        "check_git": "Running git",
        "check_revisions": "Comparing code",
        "pull": "Fetching code",
        "install_requirements": "Installing packages",
        "tests": "Running tests",
    }
    failed_messages = {
        "check_connection": "No Internet connection!",
        "check_git": "Git binary not found!",
        "check_revisions": "Exception while comparing revisions!",
        "pull": "Couldn't get new code!",
        "install_requirements": "Failed to install new packages!",
        "tests": "Tests failed!"
    }

    def do_check_git(self):
        if not GitInterface.git_available():
            logger.exception("Couldn't execute git - not found?")
            raise OSError()

    def do_check_revisions(self):
        GitInterface.command("fetch")
        current_branch_name = GitInterface.get_current_branch()
        current_revision = GitInterface.get_head_for_branch(current_branch_name)
        remote_revision = GitInterface.get_head_for_branch("origin/"+current_branch_name)
        if current_revision == remote_revision:
            raise UpdateUnnecessary
        else:
            self.previous_revision = current_revision

    def do_check_connection(self):
        conn = httplib.HTTPConnection("github.com", timeout=10)
        try:
            conn.request("HEAD", "/")
        except:
            raise
        finally:
            conn.close()

    def do_install_requirements(self):
        output = check_output(["pip", "install", "-r", "requirements.txt"])
        logger.debug("pip output:")
        logger.debug(output)

    def do_pull(self):
        current_branch_name = GitInterface.get_current_branch()
        GitInterface.pull(branch = current_branch_name)

    def do_pretest_migrations(self):
        import pretest_migrations
        pretest_migrations.main()

    def revert_pretest_migrations(self):
        import pretest_migrations
        if hasattr(pretest_migrations, 'revert'):
            pretest_migrations.revert()

    def do_tests(self):
        with open('test_commandline', 'r') as f:
            commandline = f.readline().strip()
        output = check_output(commandline.split(" "))
        logger.debug("pytest output:")
        logger.debug(output)

    def revert_pull(self):
        # do_check_revisions already ran, we now have the previous revision's
        # commit hash in self.previous_revision
        GitInterface.command("reset --hard {}".format(self.previous_revision))
        # requirements.txt now contains old requirements, let's install them back
        self.do_install_requirements()

    def pick_branch(self):
        #TODO: add branches dynamically instead of having a whitelist
        available_branches = [["master"], ["devel"]]
        branch = Listbox(available_branches, i, o, name="Git updater listbox").activate()
        if branch:
            try:
                GitInterface.checkout(branch)
            except:
                PrettyPrinter("Couldn't check out the {} branch! Try resolving the conflict through the command-line.".format(branch), i, o, 3)
            else:
                PrettyPrinter("Now on {} branch!".format(branch), i, o, 2)
                self.suggest_restart()
                #TODO: run tests?


i = None  # Input device
o = None  # Output device

def init_app(input, output):
    global i, o
    i = input
    o = output
    logging_ui.i = i
    logging_ui.o = o

def callback():
    git_updater = GitUpdater()
    c = [["Update ZPUI", git_updater.update],
         ["Select branch", git_updater.pick_branch],
         #["Submit logs", logging_ui.submit_logs],
         ["Logging settings", logging_ui.config_logging]]
    Menu(c, i, o, "ZPUI settings menu").activate()
