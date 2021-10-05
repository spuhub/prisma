import sys
import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

class OutputWindow (QtWidgets.QDialog):
    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self):
        super(OutputWindow, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'output_window.ui'), self)

        self.btn_continuar.clicked.connect(self.next)

    def next(self):
        self.hide()
        self.continue_window.emit()