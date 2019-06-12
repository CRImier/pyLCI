class Action(object):
    name = None
    func = None
    type = None
    default_affects_backlight = True
    default_will_context_switch = True

    def __init__(self, name, func, type="simple", \
                 menu_name = None, description = None, \
                 affects_backlight = None, \
                 will_context_switch = None, \
                 **kwargs):
        self.name = name
        self.func = func
        self.type = type
        self.menu_name = menu_name
        self.description = description
        self.will_context_switch = will_context_switch \
          if will_context_switch is not None \
          else self.default_will_context_switch
        self.affects_backlight = affects_backlight \
          if affects_backlight is not None \
          else self.default_affects_backlight
        kwargs.pop("context", None)
        for key, value in kwargs.items():
            setattr(self, key, value)

class BackgroundAction(Action):
    default_affects_backlight = False
    default_will_context_switch = False

class FirstBootAction(Action):
    pass

class ContextSwitchAction(Action):
    def __init__(self, name, func, **kwargs):
       Action.__init__(self, name, func, **kwargs)
       if not hasattr(self, "target_context"):
          self.target_context = None
