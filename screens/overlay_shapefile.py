import sys
import os.path

import geopandas as gpd

from qgis.PyQt.QtWidgets import QAction, QFileDialog

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

# from ..databases.shp_tools import ShpTools

class OverlayShapefile (QtWidgets.QDialog):
    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal(dict)

    def __init__(self, iface):
        self.iface = iface
        super(OverlayShapefile, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'overlay_shapefile.ui'), self)

        self.btn_voltar.clicked.connect(self.back)
        self.btn_input.clicked.connect(self.handle_input)
        self.btn_continuar.clicked.connect(self.next)

    def handle_input(self):
        self.path_shp_input = QFileDialog.getOpenFileName(self, "Selecione um arquivo SHP de entrada", '*.shp')[0]
        self.txt_input.setText(self.path_shp_input)
        return self.path_shp_input

    def back(self):
        self.hide()
        self.back_window.emit()

    def next(self):
        self.path_input = self.txt_input.text()
        # Testa se o diretório do shp de entrada foi inserido
        if (self.path_input != ""):
            # Testa se o shp de entrada possui os campos obrigatórios
            shp_input = gpd.read_file(self.path_input)
            if 'cpf_cnpj' and 'logradouro' in shp_input:
                self.hide()
                data = {"operation": "shapefile", "input": self.path_input}

                # Caso usuário tenha inserido área de aproximação
                if self.txt_aproximacao.text() != '' and float(self.txt_aproximacao.text()) > 0:
                    data['aproximacao'] = float(self.txt_aproximacao.text())

                self.continue_window.emit(data)
            else:
                self.iface.messageBar().pushMessage("Error", "O shapefile de entrada não possui os dados de entrada obrigatórios.", level=1)

        else:
            self.iface.messageBar().pushMessage("Error", "Selecione um shapefile de entrada.", level=1)
