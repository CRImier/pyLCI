from __future__ import print_function

from wm import window_manager
from menu import menu

from time import sleep

Menu = menu.Menu

class WindowManagerMenu(Menu):

    def init(self):
        self.wm.activate_wm_menu = self.to_foreground
        self.wm.deactivate_wm_menu = self.to_background
        self.listener._set_wm_callback('KEY_KPSLASH', 'deactivate_active_app', self.wm)

    def activate(self):
        Menu.activate(self)

    def to_foreground(self):
        Menu.to_foreground(self)
        self.refresh_elements()

    def refresh(self):
        self.refresh_elements()
        Menu.refresh(self)

    def refresh_elements(self):
        self.contents = self.make_menu_items()

    def select_element(self):
        Menu.select_element(self)    
        
    def deactivate(self):
        Menu.deactivate(self)

    def move_up(self):
        Menu.move_up(self)

    def move_down(self):
        Menu.move_down(self)

    def make_menu_items(self):
        app_list = self.wm.get_app_list()
        menu_items = []
        for index, app in enumerate(app_list): #those app numbers might be a possibility for a disaster, TODO
            app_item = [app.name, self.select_app_wrapper]
            menu_items.append(app_item)
        return menu_items

    def select_app_wrapper(self):
        self.select_app(self.pointer)

    def select_app(self, number):
        print(self.pointer)
        print("App number {0} selected".format(number))
        self.to_background
        self.wm.activate_app(number)
        while self.wm.active_app != None:
            sleep(1)
        print("Finished, going back to menu")
