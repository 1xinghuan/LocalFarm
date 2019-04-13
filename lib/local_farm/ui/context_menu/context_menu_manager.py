# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 11/24/2018


class ContextMenuManager(object):
    item_action_connection = {}
    registered_actions = {}

    @classmethod
    def register_actions(cls, item_name, actions=[]):
        if item_name not in cls.item_action_connection:
            cls.item_action_connection[item_name] = []
        for action in actions:
            if action not in cls.item_action_connection[item_name]:
                cls.item_action_connection[item_name].append(action)

            if action.name not in cls.registered_actions:
                cls.registered_actions[action.name] = action

    @classmethod
    def register_items_to(cls, action, items=[]):
        for item_name in items:
            cls.register_actions(item_name, [action])

    @classmethod
    def get_actions(cls, items):
        actions = []

        for item in items:
            if hasattr(item, 'itemName'):
                item_name = item.itemName
                registered_actions = cls.item_action_connection.get(item_name, [])
                for index, action in enumerate(registered_actions):
                    if isinstance(action, type):
                        registered_actions.remove(action)
                        action = action()
                        registered_actions.insert(index, action)
                        cls.registered_actions[action.name] = action
                    if action.check(items) and action not in actions:
                        actions.append(action)

        return actions

    @classmethod
    def get_action(cls, action_name):
        return cls.registered_actions.get(action_name)


class ContextAction(object):
    name = None

    def __init__(self, menu='', label=''):
        super(ContextAction, self).__init__()

        self.menu = menu
        self.label = label
        self.is_executable = True

    def check(self, items):
        self.is_executable = self.check_executable(items)
        return self.check_visible(items)

    def check_visible(self, items):
        if len(items) > 0:
            return True
        else:
            return False

    def check_executable(self, items):
        return True

    def execute(self, items):
        print(items)
