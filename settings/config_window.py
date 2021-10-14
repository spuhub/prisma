import sys
import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

from .config_layers import ConfigLayers


class ConfigWindow (QtWidgets.QDialog):

    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self):
        super(ConfigWindow, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'config_window.ui'), self)

        self.btn_cancelar.clicked.connect(self.back)
        self.btn_salvar.clicked.connect(self.next)
        self.testar_base_carregar_camadas.clicked.connect(self.hideLayerConf)

    def back(self):
        self.hide()
        self.back_window.emit()

    def next(self):
        self.hide()
        self.continue_window.emit()

    def hideLayerConf(self):
        d = ConfigLayers()
        d.exec_()

