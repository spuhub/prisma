import sys
import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

class MainWindow (QtWidgets.QDialog):

    switch_config = QtCore.pyqtSignal()
    switch_overlay_point = QtCore.pyqtSignal()
    switch_overlay_feature = QtCore.pyqtSignal()
    switch_overlay_shapefile = QtCore.pyqtSignal()
    switch_overlay_coordinates = QtCore.pyqtSignal()

    def __init__(self, iface):
        self.iface = iface
        super(MainWindow, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'main_window.ui'), self)

        self.btn_config.clicked.connect(self.go_to_config)
        self.btn_ponto.clicked.connect(self.go_to_point)
        self.btn_feicao.clicked.connect(self.go_to_feature)
        self.btn_shapefile.clicked.connect(self.go_to_shapefile)
        self.btn_shapefile.clicked.connect(self.go_to_shapefile)

    # Abre tela com busca de sobreposição utilizando arquivos shapefiles
    def go_to_shapefile(self):
        self.switch_overlay_shapefile.emit()

    # Abre a tela para busca de sobreposição através de uma feição selecionada no QGis
    def go_to_feature(self):
        if (self.iface.activeLayer() != None and self.iface.activeLayer().selectedFeatures() != []):
            self.switch_overlay_feature.emit()
        else:
            self.iface.messageBar().pushMessage("Error", "Selecione uma feição para entrada.", level=1)

    # Abre a tela com busca de sobreposição utilizando endereço ou coordenadas (lat e lon)
    def go_to_point(self):
        self.switch_overlay_point.emit()

    # Abre a tela de configuração
    def go_to_config(self):
        self.switch_config.emit()