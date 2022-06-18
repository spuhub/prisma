import sys
import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi
from qgis.utils import reloadPlugin

class MainWindow (QtWidgets.QDialog):
    """Classe que manipula a tela principal do Prisma."""

    switch_config = QtCore.pyqtSignal()
    switch_overlay_point = QtCore.pyqtSignal()
    switch_overlay_feature = QtCore.pyqtSignal()
    switch_overlay_shapefile = QtCore.pyqtSignal()
    switch_overlay_coordinates = QtCore.pyqtSignal()

    def __init__(self, iface):
        """Método construtor da classe."""
        self.iface = iface
        super(MainWindow, self).__init__()
        self.ui = loadUi(os.path.join(os.path.dirname(__file__), 'main_window.ui'), self)

        self.btn_config.clicked.connect(self.go_to_config)
        self.btn_ponto.clicked.connect(self.go_to_point)
        self.btn_feicao.clicked.connect(self.go_to_feature)
        self.btn_shapefile.clicked.connect(self.go_to_shapefile)
        self.btn_shapefile.clicked.connect(self.go_to_shapefile)
        self.ui.closeEvent = self.close_event

    def close_event(self, a):
        reloadPlugin('prisma')

    def go_to_shapefile(self):
        """Abre tela com busca de sobreposição utilizando arquivos shapefiles."""
        self.switch_overlay_shapefile.emit()

    def go_to_feature(self):
        """Abre a tela para busca de sobreposição através de uma feição selecionada no QGis."""
        if (self.iface.activeLayer() != None and self.iface.activeLayer().selectedFeatures() != []):
            self.switch_overlay_feature.emit()
        else:
            self.iface.messageBar().pushMessage("Error", "Selecione uma feição para entrada.", level=1)

    def go_to_point(self):
        """Abre a tela com busca de sobreposição utilizando endereço ou coordenadas (lat e lon)"""
        self.switch_overlay_point.emit()

    def go_to_config(self):
        """Abre a tela de configuração."""
        self.switch_config.emit()