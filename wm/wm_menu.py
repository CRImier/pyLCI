from menu import menu

Menu = menu.Menu

class WindowManagerMenu(Menu):

    def init(self):
        self.wm.activate_wm_menu = self.to_foreground
        self.wm.deactivate_wm_menu = self.to_background

    def refresh_elements(self):
        self.contents = self.make_menu_items()

    def select_element(self):
        self.refresh_elements()
        Menu.select_element(self)    

    def deactivate(self):
        Menu.deactivate(self)

    def move_up(self):
        self.refresh_elements()
        Menu.move_up(self)

    def move_down(self):
        self.refresh_elements()
        Menu.move_down(self)
        self.refresh()

    def make_menu_items(self):
        app_list = self.wm.get_app_list()
        menu_items = []
        for index, app in enumerate(app_list):
            app_item = [app.name, lambda: self.select_app(index)]
            menu_items.append(app_item)
        return menu_items

    def select_app(self, number):
        print("App number {0} selected".format(number))

    def select_element_wrapper(self):
        if position == len(app_list): #Cancel option selected
            self.deactivate()
        app_number = position
        if true:
           pass

    def activate(self):
        Menu.activate(self)        
