import sys
import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi


class ConfigLayers (QtWidgets.QDialog):

    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self):
        super(ConfigLayers, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'config_layers.ui'), self)

        self.btn_layer_cancelar.clicked.connect(self.back)
        self.btn_layer_salvar.clicked.connect(self.next)

    def back(self):
        self.hide()
        self.back_window.emit()

    def next(self):
        self.hide()
        self.continue_window.emit()