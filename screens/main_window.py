import sys
import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi
from qgis.utils import reloadPlugin

from PyQt5.QtWidgets import QShortcut, QMessageBox
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt

from ..settings.install_dependecies import instala_dependencias, verifica_flag_dependencias
from ..utils.pre_config_json import pre_config_json

## EMPACOTAMENTO DE BIBLIOTECAS ##
# Importa a biblioteca PyPDF2 da pasta da pasta libs do Prisma
current_dir = os.path.dirname(__file__)
plugin_dir = os.path.abspath(os.path.join(current_dir, '..'))
libs_dir = os.path.join(plugin_dir, 'libs')
sys.path.append(os.path.normpath(libs_dir))

arq_dependencias = os.path.join(os.path.dirname(os.path.dirname(__file__)),'settings', 'dependencies')
flag_dependencias = os.path.join(os.path.dirname(os.path.dirname(__file__)),'settings','flag_dependencies')

class MainWindow (QtWidgets.QDialog):
    """Classe que manipula a tela principal do Prisma."""

    switch_config = QtCore.pyqtSignal()
    switch_overlay_point = QtCore.pyqtSignal()
    switch_overlay_feature = QtCore.pyqtSignal()
    switch_overlay_shapefile = QtCore.pyqtSignal()
    switch_overlay_coordinates = QtCore.pyqtSignal()
    switch_memorial_conversion = QtCore.pyqtSignal()

    def __init__(self, iface):
        """Método construtor da classe."""
        self.iface = iface
        super(MainWindow, self).__init__()

        self.ui = loadUi(os.path.join(os.path.dirname(__file__), 'main_window.ui'), self)
        
        # Se False, dependencias ainda não instaladas
        if verifica_flag_dependencias(flag_dependencias) == "False":
            # Aproveita a função para realizar a pré-configuração do arquivo json
            pre_config_json()

            # msg = QMessageBox(self)
            # ret = msg.question(self, 'Download Dependências ', "É necessario fazer o download de algumas dependências para o Prisma funcionar corretamente! Deseja fazer o Download das Dependências?", QMessageBox.Yes | QMessageBox.Cancel)
            # if ret == QMessageBox.Yes:
            #    instala_dependencias(arq_dependencias)
            with open(flag_dependencias, "w", encoding='utf-8') as file:
                file.write("True")
                 
            #    ret = msg.question(self, 'Reinicio do Sistema Necessário', "É necessario fechar o QGIS para aplicar as instalações", QMessageBox.Ok)
            #    sys.exit()
        
        self.btn_config.clicked.connect(self.go_to_config)
        self.btn_ponto.clicked.connect(self.go_to_point)
        self.btn_feicao.clicked.connect(self.go_to_feature)
        self.btn_shapefile.clicked.connect(self.go_to_shapefile)
        self.btn_memorial.clicked.connect(self.go_to_memorial)

        self.ui.closeEvent = self.close_event
        self.control = 1

        # Desabilita a tecla ESC
        self.shortcut_esc = QShortcut(QKeySequence(Qt.Key_Escape), self.iface.mainWindow())
        self.shortcut_esc.setContext(Qt.ApplicationShortcut)
        self.shortcut_esc.activated.connect(self.close_event)


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

    def go_to_memorial(self):
        self.switch_memorial_conversion.emit()