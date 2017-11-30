# -*- coding: utf-8 -*-

from subprocess import call
from apps.zero_app import ZeroApp
from ui import Menu, Printer


class SkeletonApp(ZeroApp):
    def __init__(self, i, o):
        """gets called when ZPUI is starting"""
        super(SkeletonApp, self).__init__(i, o)  # call to base class constructor so input and outputs are saved
        self.menu_name = "Class Based Skeleton"  # App name as seen in main menu while using the system
        self.main_menu_contents = [
            ["Internal command", self.call_internal],
            ["External command", self.call_external],
            ["Exit", 'exit']]

    def on_start(self):
        """gets called when application is activated in the main menu"""
        super(SkeletonApp, self).on_start()  # call to base class method. Not mandatory but good practice
        Menu(self.main_menu_contents, self.i, self.o, "Skeleton app menu").activate()

    def call_internal(self):
        Printer(["Calling internal", "command"], self.i, self.o, 1)
        print("Success")

    def call_external(self):
        Printer(["Calling external", "command"], self.i, self.o, 1)
        call(['echo', 'Success'])
