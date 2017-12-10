class ZeroApp(object):
    """
    A template class for a Zerophone App. Presents default functions that are called by the app manager.
    Keeps a pointer to the input and output devices
    """

    def __init__(self, i, o):
        """ctor : called when the ZPUI boots. Avoid loading too many objects here. The application is not yet
        opened. Without knowing if you app will be used, do not burden the poor CPU with unused stuff."""
        # type: (InputListener, object) -> ZeroApp
        self.__output = o
        self.__input = i
        if not hasattr(self, "menu_name"):
            self.menu_name = "ZeroApp template"  # Name as presented in the menu

    @property
    def i(self):
        return self.__input

    @property
    def o(self):
        return self.__output

    def on_start(self):
        """
        Called ONCE when the app is selected FOR THE FIRST TIME in the menu
        """
        pass
