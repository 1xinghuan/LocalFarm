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


class DataAction(ContextAction):
    def get_selected_datas(self, items):
        dataTableWidget = items[0].tableWidget()
        selectedJobs = dataTableWidget.get_selected_datas()
        return selectedJobs


class JobAction(DataAction):
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
        from local_farm.ui.main_window import get_main_window
        mainWindow = get_main_window()
        selectedJobs = self.get_selected_datas(items)
        for job in selectedJobs:
            mainWindow.start_job(job)
            # mainWindow.update_job(job)


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
        from local_farm.ui.main_window import get_main_window
        mainWindow = get_main_window()
        selectedJobs = self.get_selected_datas(items)
        for job in selectedJobs:
            mainWindow.kill_job(job)
            mainWindow.update_data(job)


class JobRetryAction(JobAction):
    name = 'retry_job'

    def __init__(self, *args, **kwargs):
        super(JobRetryAction, self).__init__(*args, **kwargs)

        self.label = 'Retry'

    def check_executable(self, items):
        for item in items:
            if item.farmData.status in [
                LOCAL_FARM_STATUS.failed,
                LOCAL_FARM_STATUS.killed,
            ]:
                return True
        return False

    def execute(self, items):
        from local_farm.ui.main_window import get_main_window
        mainWindow = get_main_window()
        selectedJobs = self.get_selected_datas(items)
        for job in selectedJobs:
            mainWindow.retry_job(job)
            # mainWindow.update_job(job)


class JobRemoveAction(JobAction):
    name = 'remove_job'

    def __init__(self, *args, **kwargs):
        super(JobRemoveAction, self).__init__(*args, **kwargs)

        self.label = 'Remove'

    def check_executable(self, items):
        for item in items:
            if item.farmData.status not in [
                LOCAL_FARM_STATUS.new,
                LOCAL_FARM_STATUS.complete,
                LOCAL_FARM_STATUS.failed,
                LOCAL_FARM_STATUS.killed,
            ]:
                return False
        return True

    def execute(self, items):
        from local_farm.ui.main_window import get_main_window
        mainWindow = get_main_window()
        selectedJobs = self.get_selected_datas(items)
        mainWindow.remove_jobs(selectedJobs)
        mainWindow.remove_job_items(items)


class JobCheckAction(JobAction):
    name = 'check_job'

    def __init__(self, *args, **kwargs):
        super(JobCheckAction, self).__init__(*args, **kwargs)

        self.label = 'Refresh'

    def execute(self, items):
        from local_farm.ui.main_window import get_main_window
        mainWindow = get_main_window()
        selectedJobs = self.get_selected_datas(items)
        for job in selectedJobs:
            job.check_self()
            mainWindow.update_data(job)


class InstanceAction(DataAction):
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
            if item.farmData.status in [
                LOCAL_FARM_STATUS.failed,
                LOCAL_FARM_STATUS.killed,
            ]:
                return True
        return False

    def execute(self, items):
        from local_farm.ui.main_window import get_main_window
        mainWindow = get_main_window()
        selectedInstances = self.get_selected_datas(items)
        for i in selectedInstances:
            mainWindow.retry_instance(i)


ContextMenuManager.register_actions(
    'DataTableItem',
    [
        JobStartAction,
        JobKillAction,
        JobRetryAction,
        JobRemoveAction,
        JobCheckAction,
        InstanceRetryAction,
    ]
)



