# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/10/2019

from local_farm.module.sqt import *
from local_farm.data.models import *
from local_farm.ui.detail.main import DetailWindow


FARM_JOB_COLUMNS = [
    {'attr': 'id', 'label': 'Id', 'width': 70},
    {'attr': 'status', 'label': 'Status'},
    {'attr': 'name', 'label': 'Name', 'width': 400},
    {'attr': 'submitTime', 'label': 'Submit Time'},
    {'attr': 'startTime', 'label': 'Start Time'},
    {'attr': 'completeTime', 'label': 'Complete Time'},
    {'attr': 'elapsedTime', 'label': 'Elapsed Time'},
    {'attr': 'frameRange', 'label': 'Frame Range'},
]
FARM_INSTANCE_COLUMNS = [
    {'attr': 'id', 'label': 'Id', 'width': 70},
    {'attr': 'status', 'label': 'Status'},
    {'attr': 'frameRange', 'label': 'Frame Range'},
    {'attr': 'progress', 'label': 'progress'},
    {'attr': 'startTime', 'label': 'Start Time'},
    {'attr': 'completeTime', 'label': 'Complete Time'},
    {'attr': 'elapsedTime', 'label': 'Elapsed Time'},
]


class FarmDataTableItem(QTableWidgetItem):
    def __init__(self, text, data=None):
        super(FarmDataTableItem, self).__init__(text)

        self.data = data


class FarmDataTable(QTableWidget):
    columns = []

    def __init__(self):
        super(FarmDataTable, self).__init__()

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().hide()
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        headers = [i['label'] for i in self.columns]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        for index, columnDict in enumerate(self.columns):
            width = columnDict.get('width')
            if width is not None:
                self.setColumnWidth(index, width)

    def select_row(self, row):
        if row < self.rowCount():
            item = self.item(row, 0)
            item.setSelected(True)

    def refresh_from_data(self, dataQuery):
        self.clearContents()
        if isinstance(dataQuery, list):
            count = len(dataQuery)
        else:
            count = dataQuery.count()
        self.setRowCount(count)
        for index, data in enumerate(dataQuery):
            self.add_data_row(data, row=index)

    def add_data_row(self, data, row=0):
        for index, columnDict in enumerate(self.columns):
            attrName = columnDict.get('attr')
            value = getattr(data, attrName)
            valueString = u'{}'.format(value)

            item = FarmDataTableItem(valueString, data=data)
            self.setItem(row, index, item)

    def get_selected_datas(self):
        result = []
        selectedItems = self.selectedItems()
        for item in selectedItems:
            if item.data not in result:
                result.append(item.data)
        return result


class FarmJobTable(FarmDataTable):
    columns = FARM_JOB_COLUMNS


class FarmInstanceTable(FarmDataTable):
    columns = FARM_INSTANCE_COLUMNS



class LocalFarmWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(LocalFarmWindow, self).__init__(*args, **kwargs)

        self.init_ui()
        self.create_signal()

    def set_menu(self):
        self.fileMenu = QMenu('File', self)

        self.menuBar().addMenu(self.fileMenu)

        self.submitMenu = QMenu('Submit', self)
        self.menuBar().addMenu(self.submitMenu)

    def init_ui(self):
        self.set_menu()

        self.centerWidget = QWidget()
        self.setCentralWidget(self.centerWidget)
        self.masterLayout = QVBoxLayout()
        self.centerWidget.setLayout(self.masterLayout)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setAlignment(Qt.AlignLeft)
        self.refreshButton = QPushButton('Refresh')
        self.buttonLayout.addWidget(self.refreshButton)

        self.jobsTable = FarmJobTable()
        self.instancesTable = FarmInstanceTable()
        self.detailWidndow = DetailWindow()

        self.leftSplitter = QSplitter(Qt.Vertical)
        self.leftSplitter.addWidget(self.jobsTable)
        self.leftSplitter.addWidget(self.instancesTable)
        self.leftSplitter.setStretchFactor(0, 4)
        self.leftSplitter.setStretchFactor(1, 1)

        self.mainSplitter = QSplitter()
        self.mainSplitter.addWidget(self.leftSplitter)
        self.mainSplitter.addWidget(self.detailWidndow)
        self.mainSplitter.setStretchFactor(0, 2)
        self.mainSplitter.setStretchFactor(1, 1)

        self.masterLayout.addLayout(self.buttonLayout)
        self.masterLayout.addWidget(self.mainSplitter)

        self.resize(1000, 700)

    def create_signal(self):
        self.refreshButton.clicked.connect(self.refresh_clicked)
        self.jobsTable.itemSelectionChanged.connect(self.job_selected_changed)
        self.instancesTable.itemSelectionChanged.connect(self.instance_selected_changed)

    def refresh_clicked(self):
        self.refresh_job_table()

    def refresh_job_table(self):
        query = FarmJob.select().limit(50)
        self.jobsTable.refresh_from_data(query)

    def job_selected_changed(self):
        selectedJobs = self.jobsTable.get_selected_datas()
        if len(selectedJobs) > 0:
            self.refresh_instance_table(selectedJobs[0])

    def instance_selected_changed(self):
        selectedInstances = self.instancesTable.get_selected_datas()
        if len(selectedInstances) > 0:
            self.refresh_detail_window(selectedInstances[0])

    def refresh_instance_table(self, job):
        query = (FarmInstance.select(FarmInstance, FarmJob)
                 .join(FarmJob)
                 .where(FarmInstance.job == job.id)
                 .order_by(FarmInstance.id)
                 )
        self.instancesTable.refresh_from_data(query)
        self.instancesTable.select_row(0)

    def refresh_detail_window(self, instance):
        self.detailWidndow.set_instance(instance)
