import sys
import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

from ..settings.handle_json import HandleJson
from ..dbtools.shptools import HandleShapefile

class SelectDatabases(QtWidgets.QDialog):
    cancel_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self, operation_data):
        self.operation_data = operation_data
        self.handle_json = HandleJson()
        self.data_shp = self.handle_json.HandleShapefile()

        super(SelectDatabases, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'select_databases.ui'), self)

        self.check_bd.clicked.connect(self.handle_combo_bd)
        self.check_shapefile.clicked.connect(self.handle_combo_shapefile)
        self.btn_cancel.clicked.connect(self.cancel)
        self.btn_continuar.clicked.connect(self.next)
        self.combo_shapefile.currentIndexChanged.connect(self.update_shp_list)

        self.load_data_combobox()

    def update_shp_list(self):
        self.list_shapefile.clear()

        for data in self.data_shp:
            if(self.combo_shapefile.currentText() == data['nome']):
                self.list_shapefile.addItems([data['nomeFantasiaCamada']])
                self.list_shapefile.setCurrentRow(0)

    def load_data_combobox(self):
        self.combo_shapefile.addItems([data['nome'] for data in self.data_shp])

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
            indexCombo = self.combo_shapefile.currentIndex() - 1

            # Área Homologada da união e área selecionada para comparação
            areas = ["C:\\Users\\vinir\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\spu_intersect\\atlas\\Area_Uniao_Homologada_A.shp",
                     self.data_shp[indexCombo]['diretorioLocal']]
            self.operation_data['comparasion_shapefile'] = areas

            self.handle_shp = HandleShapefile()
            output = self.handle_shp.OverlayAnalisys(self.operation_data)


        elif(self.operation_data['operation'] == 'feature'):
            pass

        elif (self.operation_data['operation'] == 'address'):
            pass

        else:
            pass
        self.continue_window.emit()