import sys
import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

class SelectDatabases(QtWidgets.QDialog):
    cancel_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self, operation_data):
        self.operation_data = operation_data

        self.operation_data['path_shp'] = r'C:\Users\vinir\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\spu_intersect\atlas\Area_Quilombola_A.shp'

        super(SelectDatabases, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'select_databases.ui'), self)

        self.check_bd.clicked.connect(self.handle_combo_bd)
        self.check_shapefile.clicked.connect(self.handle_combo_shapefile)
        self.btn_cancel.clicked.connect(self.cancel)
        self.btn_continuar.clicked.connect(self.next)

        print(self.operation_data)

    def handle_combo_bd(self):
        if self.check_bd.isChecked():
            self.combo_bd.setEnabled(True)
            self.list_bd.setEnabled(True)
        else:
            self.combo_bd.setEnabled(False)
            self.list_bd.setEnabled(False)

    def handle_combo_shapefile(self):
        if self.check_shapefile.isChecked():
            self.combo_shapefile.setEnabled(True)
            self.list_shapefile.setEnabled(True)
        else:
            self.combo_shapefile.setEnabled(False)
            self.list_shapefile.setEnabled(False)

    def cancel(self):
        self.hide()
        self.cancel_window.emit()

    def next(self):
        self.hide()

        if (self.operation_data['operation'] == 'database'):
            pass

        if(self.operation_data['operation'] == 'shapefile'):
            pass

        elif(self.operation_data['operation'] == 'feature'):
            pass

        elif (self.operation_data['operation'] == 'address'):
            pass

        else:
            pass
        self.continue_window.emit()