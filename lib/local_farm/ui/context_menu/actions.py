# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 11/24/2018

from context_menu_manager import ContextAction, ContextMenuManager
import os
import subprocess
from local_farm.utils.const import LOCAL_FARM_STATUS


class Test1Action(ContextAction):
    name = 'test1_func'

    def __init__(self, *args, **kwargs):
        super(Test1Action, self).__init__(*args, **kwargs)

        self.label = 'Test1 Action'


ContextMenuManager.register_actions('TestItem', [Test1Action(menu='')])


class JobAction(ContextAction):
    def check_visible(self, items):
        visible = super(JobAction, self).check_visible(items)
        if not visible:
            return False

        from local_farm.data.models import FarmJob, FarmInstance
        item = items[0]
        if isinstance(item.farmData, FarmJob):
            return True
        else:
            return False


class JobStartAction(JobAction):
    name = 'start_job'

    def __init__(self, *args, **kwargs):
        super(JobStartAction, self).__init__(*args, **kwargs)

        self.label = 'Start'

    def check_executable(self, items):
        for item in items:
            if item.farmData.status == LOCAL_FARM_STATUS.new:
                return True
        return False

    def execute(self, items):
        dataTableWidget = items[0].tableWidget()
        mainWindow = dataTableWidget.parent()
        print mainWindow
        selectedJobs = dataTableWidget.get_selected_datas()


class JobKillAction(JobAction):
    name = 'kill_job'

    def __init__(self, *args, **kwargs):
        super(JobKillAction, self).__init__(*args, **kwargs)

        self.label = 'Kill'

    def check_executable(self, items):
        for item in items:
            if item.farmData.status == LOCAL_FARM_STATUS.running:
                return True
        return False

    def execute(self, items):
        dataTableWidget = items[0].tableWidget()
        mainWindow = dataTableWidget.parent()
        print mainWindow
        selectedJobs = dataTableWidget.get_selected_datas()


class JobRetryAction(JobAction):
    name = 'retry_job'

    def __init__(self, *args, **kwargs):
        super(JobRetryAction, self).__init__(*args, **kwargs)

        self.label = 'Retry'

    def check_executable(self, items):
        for item in items:
            if item.farmData.status == LOCAL_FARM_STATUS.failed:
                return True
        return False

    def execute(self, items):
        dataTableWidget = items[0].tableWidget()
        mainWindow = dataTableWidget.parent()
        print mainWindow
        selectedJobs = dataTableWidget.get_selected_datas()


class JobRemoveAction(JobAction):
    name = 'remove_job'

    def __init__(self, *args, **kwargs):
        super(JobRemoveAction, self).__init__(*args, **kwargs)

        self.label = 'Remove'

    def check_executable(self, items):
        for item in items:
            if item.farmData.status not in [
                LOCAL_FARM_STATUS.complete, LOCAL_FARM_STATUS.failed
            ]:
                return False
        return True

    def execute(self, items):
        dataTableWidget = items[0].tableWidget()
        mainWindow = dataTableWidget.parent()
        print mainWindow
        selectedJobs = dataTableWidget.get_selected_datas()


class InstanceAction(ContextAction):
    def check_visible(self, items):
        visible = super(InstanceAction, self).check_visible(items)
        if not visible:
            return False

        from local_farm.data.models import FarmJob, FarmInstance
        item = items[0]
        if isinstance(item.farmData, FarmInstance):
            return True
        else:
            return False


class InstanceRetryAction(InstanceAction):
    name = 'retry_instance'

    def __init__(self, *args, **kwargs):
        super(InstanceRetryAction, self).__init__(*args, **kwargs)

        self.label = 'Retry'

    def check_executable(self, items):
        for item in items:
            if item.farmData.status == LOCAL_FARM_STATUS.failed:
                return True
        return False

    def execute(self, items):
        dataTableWidget = items[0].tableWidget()
        mainWindow = dataTableWidget.parent()
        print mainWindow
        selectedJobs = dataTableWidget.get_selected_datas()


ContextMenuManager.register_actions(
    'DataTableItem',
    [
        JobStartAction,
        JobKillAction,
        JobRetryAction,
        JobRemoveAction,
        InstanceRetryAction,
    ]
)



