# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/13/2019

import json
from local_farm.module.sqt import *
from local_farm.utils.time_utils import *
from local_farm.data.models import FarmJob


class FarmPropertyWindow(QWidget):
    def __init__(self):
        super(FarmPropertyWindow, self).__init__()

        self.instance = None
        self.job = None

        self.init_ui()

    def init_ui(self):

        self.masterLayout = QVBoxLayout()
        self.masterLayout.setAlignment(Qt.AlignTop)
        self.setLayout(self.masterLayout)

        self.jobNameLabel = QLabel()

        self.jobPropertyBox = QGroupBox('Job')
        self.jobPropertyLayout = QFormLayout()
        self.jobPropertyLayout.setLabelAlignment(Qt.AlignRight)
        self.jobPropertyBox.setLayout(self.jobPropertyLayout)

        self.jobStatusLabel = QLabel('Status: ')
        self.jobProgressLabel = QLabel('Progress: ')
        self.jobSubmitTimeLabel = QLabel('Submit Time: ')
        self.jobStartTimeLabel = QLabel('Start Time: ')
        self.jobCompleteTimeLabel = QLabel('Complete Time: ')
        self.jobElapsedTimeLabel = QLabel('Elapsed Time: ')

        for i in [
            self.jobStatusLabel,
            self.jobProgressLabel,
            self.jobSubmitTimeLabel,
            self.jobStartTimeLabel,
            self.jobCompleteTimeLabel,
            self.jobElapsedTimeLabel,
        ]:
            self.jobPropertyLayout.addRow(i.text(), i)

        self.instancePropertyBox = QGroupBox('Instance')
        self.instancePropertyLayout = QFormLayout()
        self.instancePropertyLayout.setLabelAlignment(Qt.AlignRight)
        self.instancePropertyBox.setLayout(self.instancePropertyLayout)

        self.instanceStatusLabel = QLabel('Status: ')
        self.instanceProgressLabel = QLabel('Progress: ')
        self.instanceStartTimeLabel = QLabel('Start Time: ')
        self.instanceCompleteTimeLabel = QLabel('Complete Time: ')
        self.instanceElapsedTimeLabel = QLabel('Elapsed Time: ')

        for i in [
            self.instanceStatusLabel,
            self.instanceProgressLabel,
            self.instanceStartTimeLabel,
            self.instanceCompleteTimeLabel,
            self.instanceElapsedTimeLabel,
        ]:
            self.instancePropertyLayout.addRow(i.text(), i)

        self.masterLayout.addWidget(self.jobNameLabel)
        self.masterLayout.addWidget(self.jobPropertyBox)
        self.masterLayout.addWidget(self.instancePropertyBox)

    def set_instance(self, instance, job=None):
        self.instance = instance
        self.job = job
        if job is None:
            self.job = self.instance.job

        self.update_ui()

    def update_ui(self):
        self.jobNameLabel.setText(u'{}'.format(self.job.name))
        self.jobStatusLabel.setText(self.job.status)
        self.jobProgressLabel.setText('{}'.format(self.job.progress))
        self.jobSubmitTimeLabel.setText(datetime_to_str(self.job.submitTime))
        self.jobStartTimeLabel.setText(datetime_to_str(self.job.startTime))
        self.jobCompleteTimeLabel.setText(datetime_to_str(self.job.completeTime))
        self.jobElapsedTimeLabel.setText(get_detail_time_delta(self.job.elapsedTime))

        self.instanceStatusLabel.setText(self.instance.status)
        self.instanceProgressLabel.setText('{}'.format(self.instance.progress))
        self.instanceStartTimeLabel.setText(datetime_to_str(self.instance.startTime))
        self.instanceCompleteTimeLabel.setText(datetime_to_str(self.instance.completeTime))
        self.instanceElapsedTimeLabel.setText(get_detail_time_delta(self.instance.elapsedTime))


class AutoResizeTextEdit(QTextBrowser):
    def __init__(self, *args, **kwargs):
        super(AutoResizeTextEdit, self).__init__(*args, **kwargs)

        self.setReadOnly(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def set_size(self):
        target_height = self.document().size().height()
        self.setFixedHeight(target_height + 5.0)

    def resizeEvent(self, event):
        super(AutoResizeTextEdit, self).resizeEvent(event)
        self.set_size()


class FarmCommandWindow(QScrollArea):
    def __init__(self):
        super(FarmCommandWindow, self).__init__()

        self.instance = None
        self.job = None

        self.init_ui()

    def init_ui(self):
        self.centerWidget = QWidget()
        self.masterLayout = QVBoxLayout()
        self.centerWidget.setLayout(self.masterLayout)
        self.setWidget(self.centerWidget)
        self.setWidgetResizable(True)

        self.commandEdit = AutoResizeTextEdit()
        self.commandEdit.setReadOnly(True)
        self.frameRangeLabel = QLabel()
        self.cwdLabel = QLabel()
        self.envEdit = AutoResizeTextEdit()
        self.envEdit.setReadOnly(True)
        self.envEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.add_row('Command: ', self.commandEdit)
        self.add_row('Frame Range: ', self.frameRangeLabel)
        self.add_row('Cwd: ', self.cwdLabel)
        self.add_row('Env: ', self.envEdit)

    def add_row(self, label, widget):
        label = QLabel(label)
        layout1 = QVBoxLayout()
        layout1.setAlignment(Qt.AlignTop)
        layout1.addWidget(label)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft)
        layout.addLayout(layout1)
        layout.addWidget(widget)
        self.masterLayout.addLayout(layout)

    def set_instance(self, instance, job=None):
        self.instance = instance
        self.job = job
        if job is None:
            self.job = self.instance.job

        self.update_ui()

    def update_ui(self):
        self.commandEdit.setText(self.job.command)
        self.frameRangeLabel.setText(self.instance.frameRange or '')
        self.cwdLabel.setText(self.job.cwd or '')
        env = self.job.env
        envStr = json.dumps(
            env,
            sort_keys=True,
            indent=4,
            separators=(',', ': '),
            encoding="utf-8",
            ensure_ascii=False
        )
        self.envEdit.setText(envStr)


class FarmLogWindow(QTabWidget):
    def __init__(self):
        super(FarmLogWindow, self).__init__()

        self.stdoutEdit = QTextEdit()
        self.stderrEdit = QTextEdit()

        self.addTab(self.stdoutEdit, 'stdout')
        self.addTab(self.stderrEdit, 'stderr')

    def set_instance(self, instance, job=None):
        self.instance = instance
        self.job = job
        if job is None:
            self.job = self.instance.job

        self.update_ui()

    def update_ui(self):
        self.stdoutEdit.setText(self.instance.stdout or '')
        self.stderrEdit.setText(self.instance.stderr or '')


class DetailWindow(QTabWidget):
    def __init__(self):
        super(DetailWindow, self).__init__()

        self.propertyWindow = FarmPropertyWindow()
        self.commandWindow = FarmCommandWindow()
        self.logWindow = FarmLogWindow()

        self.addTab(self.propertyWindow, 'Property')
        self.addTab(self.commandWindow, 'Command')
        self.addTab(self.logWindow, 'Log')

    def set_instance(self, instance):
        job = FarmJob.get(id=instance.job)
        self.propertyWindow.set_instance(instance, job=job)
        self.commandWindow.set_instance(instance, job=job)
        self.logWindow.set_instance(instance, job=job)


