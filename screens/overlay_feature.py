import sys
import os.path

import geopandas as gpd

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

class OverlayFeature (QtWidgets.QDialog):

    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self, iface):
        self.iface = iface
        super(OverlayFeature, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'overlay_feature.ui'), self)

        self.btn_voltar.clicked.connect(self.back)
        self.btn_continuar.clicked.connect(self.next)
        self.get_selected_features()

    def back(self):
        self.hide()
        self.back_window.emit()

    def next(self):
        self.hide()
        self.continue_window.emit()

    def get_selected_features(self):
        layer = self.iface.activeLayer()
        selected_features = layer.selectedFeatures()

        for feature in range(len(selected_features)):
            print("Fields: ", selected_features[0].fields().names())
            print("Atributes: ", selected_features[0].attributes())
            print("Geometry: ", selected_features[0].geometry())

        # selected_features.append(geometry)
        # print(selected_features)
        # gdf = gpd.GeoDataFrame