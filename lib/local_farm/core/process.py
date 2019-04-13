# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/12/2019

import os
import subprocess
import datetime
from local_farm.module.sqt import QThread, Signal
from local_farm.utils.const import LOCAL_FARM_STATUS, LOCAL_FARM_VARIABLES
from local_farm.utils.frame import get_frame_info


class ProcessThread(QThread):
    progressChanged = Signal(int)
    processDone = Signal()

    def __init__(self, instance):
        super(ProcessThread, self).__init__()

        self.instance = instance
        self.job = self.instance.job

        self.pid = None

    def run(self):
        cmd = self.job.commandLine
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

        startTime = datetime.datetime.now()

        self.instance.startTime = startTime
        self.instance.status = LOCAL_FARM_STATUS.running
        self.instance.save()

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

        stdout = process.stdout.readline()

        while stdout:
            print stdout
            stdoutData = self.instance.stdout
            stdoutData += stdout
            self.instance.stdout = stdoutData
            self.instance.save()

            stdout = process.stdout.readline()

        stderr = process.stderr.readline()

        while stderr:
            print stderr
            stderrData = self.instance.stderr
            stderrData += stderr
            self.instance.stderr = stderrData

            stderr = process.stderr.readline()

            failed = True


        completeTime = datetime.datetime.now()
        elapsedTime = completeTime - startTime
        elapsedTime = int(elapsedTime.total_seconds())

        self.instance.completeTime = completeTime
        self.instance.elapsedTime = elapsedTime

        if failed:
            self.instance.status = LOCAL_FARM_STATUS.failed
        else:
            self.instance.status = LOCAL_FARM_STATUS.complete

        self.instance.save()

        self.processDone.emit()




