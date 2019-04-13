# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 11/24/2018


from local_farm.module.sqt import *
from context_menu_manager import ContextMenuManager
import actions


class ContextObject(object):
    def __init__(self):
        super(ContextObject, self).__init__()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu_requested)

    def context_menu_requested(self):
        selected_items = self.selectedItems()

        self.contextMenu = Menu(self)

        actions = ContextMenuManager.get_actions(selected_items)
        for context_action in actions:
            # if isinstance(context_action, type):
            #     context_action = context_action()
            current_menu = self.contextMenu
            menu_list = context_action.menu.split('/')
            if not (len(menu_list) == 1 and menu_list[0] == ''):
                for menu_label in menu_list:
                    current_menu = current_menu.find_or_add_menu(menu_label)

            action = QAction(context_action.label, self.contextMenu)
            action.setObjectName(context_action.name)
            action.setEnabled(context_action.is_executable)
            current_menu.addAction(action)
            action.triggered.connect(self.action_triggered)

        self.contextMenu.move(QCursor.pos())
        self.contextMenu.show()

    def action_triggered(self):
        action = self.sender()
        selected_items = self.selectedItems()
        action_name = to_unicode(action.objectName())
        context_action = ContextMenuManager.get_action(action_name)
        context_action.execute(selected_items)


class Menu(QMenu):
    def __init__(self, *args, **kwargs):
        super(Menu, self).__init__(*args, **kwargs)

    def findAction(self, name):
        for action in self.actions():
            if action.text() == name:
                return action

    def findSubMenu(self, name):
        action = self.findAction(name)
        if action is not None:
            return action.menu()
        else:
            return None
    
    def find_or_add_menu(self, name):
        menu = self.findSubMenu(name)
        if menu is None:
            menu = QMenu(name, self)
            self.addMenu(menu)
        return menu
