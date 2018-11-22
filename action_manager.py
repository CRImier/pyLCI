from copy import copy

class Action(object):
    pass

class ActionManager(object):
    def __init__(self):
        self.actions = []

    def register_action(self, **kwargs):
        self.actions.append(kwargs)

    def get_actions(self):
        return [copy(action) for action in self.actions]
