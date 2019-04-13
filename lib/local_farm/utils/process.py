# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/13/2019

import platform
import subprocess


def kill_pid(pid):
    operatingSystem = platform.system()
    if operatingSystem == "Windows":
        subprocess.Popen("taskkill /F /T /PID %s" % pid, shell=True)
    elif operatingSystem == "Linux":
        import psutil
        for p in psutil.process_iter():
            if p.pid == int(pid):
                for child in p.children():
                    for childchild in child.children():
                        os.system("kill -9 %s" % childchild.pid)
                    os.system("kill -9 %s" % child.pid)
        os.system("kill -9 %s" % pid)


