# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/12/2019

import os
import subprocess
import datetime
from local_farm.module.sqt import QThread, Signal
from local_farm.utils.const import LOCAL_FARM_STATUS, LOCAL_FARM_VARIABLES
from local_farm.utils.frame import get_frame_info
from local_farm.data.models import FarmJob, FarmInstance


class ProcessThread(QThread):
    statusChanged = Signal(object, str)
    progressChanged = Signal(int)
    processDone = Signal(object)

    def __init__(self, instance=None):
        super(ProcessThread, self).__init__()

        if instance is not None:
            self.set_instance(instance)

        self.pid = None

    def set_instance(self, instance, status=LOCAL_FARM_STATUS.pending):
        self.instance = instance
        self.instance.processThread = self
        self.job = self.instance.job

        self.pid = None

        self.instance.status = status
        self.instance.save()
        self.statusChanged.emit(self.instance, LOCAL_FARM_STATUS.pending)

        if self.job.status == LOCAL_FARM_STATUS.new:
            self.job.status = LOCAL_FARM_STATUS.pending
            self.job.save()
            self.statusChanged.emit(self.job, LOCAL_FARM_STATUS.pending)

    def get_instance(self):
        return FarmInstance.get(id=self.instance.id)

    def run(self):
        cmd = self.job.command
        cwd = self.job.cwd
        env = self.job.env
        if env is not None:
            temp = {}
            temp.update(os.environ)
            temp.update(env)
            env = temp
        callbacks = self.job.callbacks
        frameRange = self.instance.frameRange

        frameStart = ''
        frameEnd = ''
        frameInterval = ''
        frameString = ''
        if frameRange is not None:
            frameString = frameRange
            frameStart, frameEnd, frameInterval = get_frame_info(frameRange)

        cmd = cmd.replace('${}'.format(LOCAL_FARM_VARIABLES.FRAME_START), frameStart)
        cmd = cmd.replace('${}'.format(LOCAL_FARM_VARIABLES.FRAME_END), frameEnd)
        cmd = cmd.replace('${}'.format(LOCAL_FARM_VARIABLES.FRAME_INTERVAL), frameInterval)
        cmd = cmd.replace('${}'.format(LOCAL_FARM_VARIABLES.FRAME_STRING), frameString)

        failed = False

        process = subprocess.Popen(
            cmd,
            shell=True,
            cwd=cwd,
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.pid = process.pid

        startTime = datetime.datetime.now()

        self.instance.startTime = startTime
        self.instance.status = LOCAL_FARM_STATUS.running
        self.instance.pid = self.pid
        self.instance.save()

        self.statusChanged.emit(self.instance, LOCAL_FARM_STATUS.running)

        job = FarmJob.get(id=self.job.id)
        if job.status in [
            LOCAL_FARM_STATUS.pending,
            # LOCAL_FARM_STATUS.killed,
            # LOCAL_FARM_STATUS.failed,
        ]:
            job.status = LOCAL_FARM_STATUS.running
            job.save()
            self.statusChanged.emit(job, LOCAL_FARM_STATUS.running)
        if job.startTime is None:
            job.startTime = startTime
            job.save()

        stdout = process.stdout.readline()

        while stdout:
            # print(stdout)
            self.instance.write_temp_std(stdout)
            # stdoutData = self.instance.stdout or ''
            # stdoutData += stdout
            # self.instance.stdout = stdoutData
            # self.instance.save()

            stdout = process.stdout.readline()

        stderr = process.stderr.readline()

        while stderr:
            # print(stderr)
            self.instance.write_temp_std(stderr, err=True)
            # stderrData = self.instance.stderr or ''
            # stderrData += stderr
            # self.instance.stderr = stderrData

            stderr = process.stderr.readline()

            failed = True

        completeTime = datetime.datetime.now()
        elapsedTime = completeTime - startTime
        elapsedTime = int(elapsedTime.total_seconds())

        self.instance.completeTime = completeTime
        self.instance.elapsedTime = elapsedTime
        self.instance.pid = None

        self.instance.write_std()

        job = FarmJob.get(id=self.job.id)
        if failed:
            self.instance.status = LOCAL_FARM_STATUS.failed
            job.status = LOCAL_FARM_STATUS.failed
        else:
            self.instance.status = LOCAL_FARM_STATUS.complete

        self.instance.save()
        self.statusChanged.emit(self.instance, self.instance.status)

        jobComplete = False
        # print 'instance finish', job
        if not failed:
            notCompleteInstances = job.get_instances(LOCAL_FARM_STATUS.complete, reverse=True)
            if len(notCompleteInstances) == 0:
                jobComplete = True
                job.status = LOCAL_FARM_STATUS.complete
                job.completeTime = completeTime
                jobElapsedTime = completeTime - job.startTime
                jobElapsedTime = int(jobElapsedTime.total_seconds())
                job.elapsedTime = jobElapsedTime

        job.save()
        # print 'saved', job, job.status

        if jobComplete:
            for dstJob in job.destinations:
                result = dstJob.check_sources()
                if result:
                    self.statusChanged.emit(dstJob, dstJob.status)

        self.statusChanged.emit(job, job.status)

        self.processDone.emit(self)

