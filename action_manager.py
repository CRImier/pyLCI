class ActionManager(object):
    action_name_delimiter = "%"

    def __init__(self):
        self.actions = {}

    def register_action(self, action):
        name = action.full_name
        self.actions[name] = action

    def register_firstboot_action(self, context_alias, action):
        name = action.name
        if context_alias:
            name = "".join(context_alias, self.action_name_delimiter, name)
        self.actions[name] = action

    def get_actions(self):
        return self.actions

    def get_firstboot_actions(self):
        return dict([(name, action) for name, action in self.actions.items() if isinstance(action, FirstbootAction)])
