class Action(object):
    name = None
    func = None
    type = None
    affect_backlight = True
    will_context_switch = True

    def __init__(self, name, func, type="simple", \
                 affects_backlight = True, \
                 will_context_switch = True, \
                 **kwargs):
        self.name = name
        self.func = func
        self.type = type
        self.will_context_switch = will_context_switch
        self.affects_backlight = affects_backlight
        for key, value in kwargs.items():
            setattr(self, key, value)


class FirstBootAction(Action):
    pass


class ContextSwitchAction(Action):
    def __init__(self, name, func, **kwargs):
       Action.__init__(self, name, None, **kwargs)
       if not hasattr(self, "target_context"):
          raise AttributeError("Target context not passed to ContextSwitchAction constructor!")
