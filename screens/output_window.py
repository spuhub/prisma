import sys
import os.path

from qgis.PyQt.QtWidgets import QAction, QFileDialog

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

class OutputWindow (QtWidgets.QDialog):
    cancel_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self):
        super(OutputWindow, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'output_window.ui'), self)

        self.btn_output.clicked.connect(self.handle_output)
        self.btn_cancel.clicked.connect(self.cancel)
        self.btn_continuar.clicked.connect(self.next)

    def handle_output(self):
        self.output = QFileDialog.getExistingDirectory(self, "Selecione a pasta de saída")
        self.txt_output.setText(self.output)

    def cancel(self):
        self.hide()
        self.cancel_window.emit()

    def next(self):
        self.hide()
        self.continue_window.emit()