menu_name = "Settings"

import os
import signal
from time import sleep
from subprocess import check_output, CalledProcessError

try:
    import httplib
except:
    import http.client as httplib

#Using a TextProgressBar because only it shows a message on the screen for now
from ui import Menu, Printer, PrettyPrinter, DialogBox, TextProgressBar
from helpers.logger import setup_logger

logger = setup_logger(__name__, "info")

class GitInterface():

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
        return check_output(commandline, shell=True)

    @classmethod
    def get_head_for_branch(cls, branch):
        output = cls.command("rev-parse {}".format(branch)).strip()
        return output

    @classmethod
    def checkout(cls, reference):
        cls.command("checkout {}".format(reference))

    @classmethod
    def pull(cls, source = "origin", branch = "master", opts="--ff-only"):
        return cls.command("pull {2} {0} {1}".format(source, branch, opts))


class UpdateUnnecessary(Exception):
    pass


class GenericUpdater(object):

    steps = []
    progressbar_messages = {}
    failed_messages = {}

    def run_step(self, step_name):
        logger.info("Running update step: '{}'".format(step_name))
        getattr(self, "do_"+step_name)()
        logger.debug("Update step '{}' completed!".format(step_name))

    def revert_step(self, step_name):
        if hasattr(self, "revert_"+step_name):
            logger.info("Reverting update step: '{}'".format(step_name))
            getattr(self, "revert_"+step_name)()
            logger.debug("Update step '{}' reverted!".format(step_name))
        else:
            logger.debug("Can't revert step {} - no reverter available.".format(step_name))

    def update(self):
        logger.info("Starting update process")
        pb = TextProgressBar(i, o, message = "Updating ZPUI")
        pb.run_in_background()
        progress_per_step = 1.0/len(self.steps)

        completed_steps = []
        try:
            for step in self.steps:
                pb.set_message(self.progressbar_messages.get(step, "Loading..."))
                sleep(0.5) #The user needs some time to read the message
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
            pb.stop()
            PrettyPrinter(failed_message, i, o, 2)
            pb.set_message("Reverting update")
            pb.run_in_background()
            logger.info("Reverting the failed step: {}".format(failed_step))
            self.revert_step(failed_step)
            logger.info("Reverting the failed steps")
            for step in completed_steps:
                try:
                    self.revert_step(step)
                except:
                    logger.exception("Failed to revert step {}".format(failed_step))
                    pb.stop()
                    PrettyPrinter("Failed to revert step '{}'".format(step), i, o, 2)
                    pb.run_in_background()
                pb.progress -= progress_per_step
            pb.stop()
            PrettyPrinter("Update failed, try again later?", i, o, 3)
        else:
            sleep(0.5) #showing the completed progressbar
            pb.stop()
            PrettyPrinter("Update successful!", i, o, 3)
            needs_restart = DialogBox('yn', i, o, message="Restart ZPUI?").activate()
            if needs_restart:
                os.kill(os.getpid(), signal.SIGTERM)

            

class GitUpdater(GenericUpdater):
    branch = "master"

    steps = ["check_connection", "check_git", "check_revisions", "pull", "install_requirements", "tests"]
    progressbar_messages = { \
             "check_connection":"Connection check",
             "check_git":"Running git",
             "check_revisions":"Comparing code",
             "pull":"Fetching code",
             "install_requirements":"Installing packages",
             "tests":"Running tests",
             }
    failed_messages = { \
             "check_connection":"No Internet connection!",
             "check_git":"Git binary not found!",
             "check_revisions":"Exception while comparing revisions!",
             "pull":"Couldn't get new code!",
             "install_requirements":"Failed to install new packages!",
             "tests":"Tests failed!"
             }

    def do_check_git(self):
        if not GitInterface.git_available():
            logger.exception("Couldn't execute git - not found?")
            raise OSError()

    def do_check_revisions(self):
        current_revision = GitInterface.get_head_for_branch("master")
        remote_revision = GitInterface.get_head_for_branch("origin/master")
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
        GitInterface.pull()

    def do_tests(self):
        import pytest

    def revert_pull(self):
        # do_check_revisions already ran, we now have the previous revision's
        # commit hash in self.previous_revision
        GitInterface.checkout(self.previous_revision)
        # requirements.txt now contains old requirements, let's install them back
        self.do_install_requirements()

def settings():
    git_updater = GitUpdater()
    c = [["Update ZPUI", git_updater.update]]
    Menu(c, i, o, "ZPUI settings menu").activate()


callback = settings
i = None  # Input device
o = None  # Output device


def init_app(input, output):
    global i, o
    i = input; o = output
