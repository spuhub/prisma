import sys
import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi
from qgis.utils import reloadPlugin

from PyQt5.QtWidgets import QWidget, QShortcut, QApplication, QMessageBox
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

from ..dependency import Dependency


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
        self.control = 1

        # Desabilita a tecla ESC
        self.shortcut_esc = QShortcut(QKeySequence(Qt.Key_Escape), self.iface.mainWindow())
        self.shortcut_esc.setContext(Qt.ApplicationShortcut)
        self.shortcut_esc.activated.connect(self.close_event)
        self.dialog_dependecy()



    def dialog_dependecy(self):
        if not os.path.isdir(os.path.join(os.path.dirname(__file__), '../penv')):
            msg = QMessageBox(self)
            ret = msg.question(self, 'Download Dependências ', "É necessario fazer o download de algumas dependências para o Prisma funcionar corretamente! Deseja fazer o Download das Dependências?", QMessageBox.Yes | QMessageBox.Cancel)
            if ret == QMessageBox.Yes:
                print('Button QMessageBox.Yes clicked.')
                d = Dependency()
                d.exec_()
                self.control = 0
                self.ui.close()


    def close_event(self, a):
        print("teste")
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