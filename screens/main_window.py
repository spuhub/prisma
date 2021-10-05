import sys
import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

class MainWindow (QtWidgets.QDialog):

    switch_config = QtCore.pyqtSignal()
    switch_overlay_address = QtCore.pyqtSignal()
    switch_overlay_feature = QtCore.pyqtSignal()
    switch_overlay_shapefile = QtCore.pyqtSignal()
    switch_overlay_coordinates = QtCore.pyqtSignal()

    def __init__(self):

        super(MainWindow, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'main_window.ui'), self)

        self.btn_config.clicked.connect(self.go_to_config)
        self.btn_endereco.clicked.connect(self.go_to_address)
        self.btn_feicao.clicked.connect(self.go_to_feature)
        self.btn_shapefile.clicked.connect(self.go_to_shapefile)
        self.btn_shapefile.clicked.connect(self.go_to_shapefile)
        self.btn_coordinates.clicked.connect(self.go_to_coordinates)

    def go_to_config(self):
        self.switch_config.emit()

    def go_to_address(self):
        self.switch_overlay_address.emit()

    def go_to_feature(self):
        self.switch_overlay_feature.emit()

    def go_to_shapefile(self):
        self.switch_overlay_shapefile.emit()

    def go_to_coordinates(self):
        self.switch_overlay_coordinates.emit()