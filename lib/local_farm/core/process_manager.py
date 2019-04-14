# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/13/2019

from local_farm.utils.const import LOCAL_FARM_STATUS
from local_farm.core.process import ProcessThread
from local_farm.data.models import FarmJob


def process_cmp(t1, t2):
    i1 = t1.instance
    i2 = t2.instance
    if i1.id > i2.id:
        return 1
    if i1.id < i2.id:
        return -1
    return 0


class ProcessManager(object):
    def __init__(self):
        super(ProcessManager, self).__init__()

        self.runningProcessNum = 5
        self.processPool = []

    def get_process_by_status(self, status):
        if not isinstance(status, list):
            status = [status]
        result = []
        for p in self.processPool:
            if p.instance.status in status:
                result.append(p)
        return result

    def start_job(self, job):
        job.status = LOCAL_FARM_STATUS.pending
        job.save()

        instances = job.get_instances()
        self.add_instances_to_pool(instances)
        self.check_all()
        self.process_status_changed(job)

    def add_instances_to_pool(self, instances):
        for i in instances:
            self.add_instance_to_pool(i)

    def add_instance_to_pool(self, instance):
        self.processThread = ProcessThread()
        self.processThread.statusChanged.connect(self.process_status_changed)
        self.processThread.progressChanged.connect(self.process_progress_changed)
        self.processThread.processDone.connect(self.process_done)
        self.processPool.append(self.processThread)

        self.processThread.set_instance(instance)

    def check_all(self):
        self.processPool.sort(cmp=process_cmp)
        runningProcessList = self.get_process_by_status(LOCAL_FARM_STATUS.running)
        pendingProcessList = self.get_process_by_status(LOCAL_FARM_STATUS.pending)
        if len(runningProcessList) < self.runningProcessNum:
            for t in pendingProcessList[:self.runningProcessNum - len(runningProcessList)]:
                t.start()

    def process_done(self, process):
        # self.processPool.remove(process)
        self.check_all()

    def process_progress_changed(self, progress):
        pass

    def process_status_changed(self, data, status=None):
        pass

    def kill_job(self, job):
        for i in job.get_instances():
            self.kill_instance(i)

        job.status = LOCAL_FARM_STATUS.killed
        job.save()
        self.process_status_changed(job)

    def kill_instance(self, instance):
        from local_farm.utils.process import kill_pid

        i = instance
        pid = i.pid
        if pid is not None:
            kill_pid(pid)
            for t in self.processPool:
                if t.pid == pid:
                    t.terminate()

        i.pid = None

        if i.status in [
            LOCAL_FARM_STATUS.new,
            LOCAL_FARM_STATUS.pending,
            LOCAL_FARM_STATUS.running,
        ]:
            i.status = LOCAL_FARM_STATUS.killed
            i.save()
            self.process_status_changed(i)

    def retry_job(self, job):
        job.check_self()
        self.process_status_changed(job)

        instances = job.get_instances(status=[
            LOCAL_FARM_STATUS.failed,
            LOCAL_FARM_STATUS.killed,
        ])
        self.add_instances_to_pool(instances)
        self.check_all()

    def retry_instance(self, instance):
        self.add_instance_to_pool(instance)
        self.check_all()

    def remove_jobs(self, job):
        if not isinstance(job, list):
            job = [job]
        jobids = [i.id for i in job]
        FarmJob.delete().where(FarmJob.id.in_(jobids)).execute()


