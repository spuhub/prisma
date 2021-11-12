import sys
import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.uic import loadUi

from ..settings.json_tools import JsonTools
from ..dbtools.shp_tools import ShpTools

import geopandas as gpd

from qgis.core import QgsVectorLayer, QgsPoint

class SelectDatabases(QtWidgets.QDialog):
    cancel_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal(dict)

    def __init__(self, operation_data):
        self.operation_data = operation_data
        # print(self.operation_data)
        self.json_tools = JsonTools()
        self.data_bd = self.json_tools.get_config_database()
        self.data_shp = self.json_tools.get_config_shapefile()

        super(SelectDatabases, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'select_databases.ui'), self)

        # Funcionalidades dos botões da tela
        self.check_bd.clicked.connect(self.handle_check_bd)
        self.check_shp.clicked.connect(self.handle_check_shp)
        self.btn_cancel.clicked.connect(self.cancel)
        self.btn_continuar.clicked.connect(self.next)

        self.load_lists()

    # Adição de checkbox e estilização na lista de shapefiles e bancos de dados
    def load_lists(self):
        for i in range(len(self.data_shp)):
            item = QtWidgets.QListWidgetItem(self.data_shp[i]['nome'])
            item.setFont(QFont('Arial', 10))
            item.setSizeHint(QtCore.QSize(20, 30))
            item.setFlags(item.flags())
            self.list_shp.addItem(item)

        for i in range(len(self.data_bd)):
            item = QtWidgets.QListWidgetItem(self.data_bd[i]['nome'])
            item.setFont(QFont('Arial', 10))
            item.setSizeHint(QtCore.QSize(20, 30))
            item.setFlags(item.flags())
            self.list_bd.addItem(item)

    def handle_check_bd(self):
        if self.check_bd.isChecked():
            self.list_bd.setEnabled(True)
        else:
            self.list_bd.setEnabled(False)

    def handle_check_shp(self):
        if self.check_shp.isChecked():
            self.list_shp.setEnabled(True)
        else:
            self.list_shp.setEnabled(False)

    # Monta uma lista de configurações para operação que será realizada
    def create_operation_config(self, selected_items_bd, selected_items_shp):
        self.operation_data['shp'] = []
        for i in self.data_shp:
            if(i['nome'] in selected_items_shp):
                self.operation_data['shp'].append(i)

        self.operation_data['pg'] = []
        for i in self.data_bd:
            if (i['nome'] in selected_items_bd):
                self.operation_data['pg'].append(i)

        return self.operation_data

    def cancel(self):
        self.hide()
        self.cancel_window.emit()

    def next(self):
        self.hide()

        if(self.operation_data['operation'] == 'shapefile'):
            selected_items_bd = [item.text() for item in self.list_bd.selectedItems()]
            selected_items_shp = [item.text() for item in self.list_shp.selectedItems()]

            self.operation_data = self.create_operation_config(selected_items_bd, selected_items_shp)

            # Comparação com Shapefiles
            self.shp_tools = ShpTools()
            gdf_result = self.shp_tools.OverlayAnalisys(self.operation_data)
            result = {'operation': 'shapefile', 'overlay_shp': gdf_result['overlay_shp'], 'overlay_db': gdf_result['overlay_db'],
                      'input': gdf_result['input'], 'gdf_selected_shp': gdf_result['gdf_selected_shp'],
                      'gdf_selected_db': gdf_result['gdf_selected_db'], 'operation_data': self.operation_data}

            self.continue_window.emit(result)

        elif(self.operation_data['operation'] == 'feature'):
            pass

        elif (self.operation_data['operation'] == 'address'):
            pass

        else:
            # Point
            pass