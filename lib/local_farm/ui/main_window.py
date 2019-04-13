# -*- coding: utf-8 -*-
# __author__ = 'XingHuan'
# 4/10/2019

from local_farm.module.sqt import *
from local_farm.data.models import *
from local_farm.ui.detail.main import DetailWindow
from local_farm.ui.context_menu.context_object import ContextObject
from local_farm.core.process_manager import ProcessManager


_MAIN_WINDOW = None


FARM_JOB_COLUMNS = [
    {'attr': 'id', 'label': 'Id', 'width': 70},
    {'attr': 'status', 'label': 'Status'},
    {'attr': 'name', 'label': 'Name', 'width': 300},
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
    itemName = 'DataTableItem'

    def __init__(self, text, data=None):
        super(FarmDataTableItem, self).__init__(text)

        self.farmData = data
        # self.tableWidget()


class FarmDataTable(QTableWidget, ContextObject):
    columns = []

    def __init__(self, *args, **kwargs):
        super(FarmDataTable, self).__init__(*args, **kwargs)
        ContextObject.__init__(self)

        self._dataRows = {}

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
        items = []
        for index, columnDict in enumerate(self.columns):
            attrName = columnDict.get('attr')
            value = getattr(data, attrName)
            valueString = u'{}'.format(value)

            item = FarmDataTableItem(valueString, data=data)
            self.setItem(row, index, item)
            items.append(item)
        self._dataRows[data] = items

    def get_selected_datas(self):
        result = []
        selectedItems = self.selectedItems()
        for item in selectedItems:
            if item.farmData not in result:
                result.append(item.farmData)
        return result

    def get_data_items(self, data):
        return self._dataRows.get(data, [])


class FarmJobTable(FarmDataTable):
    columns = FARM_JOB_COLUMNS


class FarmInstanceTable(FarmDataTable):
    columns = FARM_INSTANCE_COLUMNS



class LocalFarmWindow(QMainWindow, ProcessManager):
    def __init__(self, *args, **kwargs):
        super(LocalFarmWindow, self).__init__(*args, **kwargs)
        ProcessManager.__init__(self)

        self.init_ui()
        self.create_signal()

        global _MAIN_WINDOW
        _MAIN_WINDOW = self

        self.refresh_job_table()

    def set_menu(self):
        self.fileMenu = QMenu('File', self)
        self.menuBar().addMenu(self.fileMenu)

        self.submitMenu = QMenu('Submit', self)
        self.menuBar().addMenu(self.submitMenu)

    def init_ui(self):
        self.setWindowTitle('Local Farm')

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

        self.resize(1300, 800)

    def create_signal(self):
        self.refreshButton.clicked.connect(self.refresh_clicked)
        self.jobsTable.itemSelectionChanged.connect(self.job_selected_changed)
        self.instancesTable.itemSelectionChanged.connect(self.instance_selected_changed)

    def refresh_clicked(self):
        self.refresh_job_table()

    def refresh_job_table(self):
        query = FarmJob.select().order_by(FarmJob.id.desc()).limit(50)
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
        query = job.get_instances()
        self.instancesTable.refresh_from_data(query)
        self.instancesTable.select_row(0)

    def refresh_detail_window(self, instance):
        self.detailWidndow.set_instance(instance)

    def update_job(self, job):
        items = self.jobsTable.get_data_items(job)
        for item in items:
            col = item.column()
            columnDict = self.jobsTable.columns[col]

            attrName = columnDict.get('attr')
            value = getattr(job, attrName)
            valueString = u'{}'.format(value)
            item.setText(valueString)

    def remove_job_items(self, items):
        rows = []
        for i in items:
            row = i.row()
            if row not in rows:
                rows.append(row)
        rows.sort(reverse=True)
        for row in rows:
            self.jobsTable.removeRow(row)


def get_main_window():
    return _MAIN_WINDOW

