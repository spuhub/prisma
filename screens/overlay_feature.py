import sys
import os.path

import geopandas as gpd

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

from qgis.utils import iface

class OverlayFeature (QtWidgets.QDialog):
    """Classe que manipula a tela de teste de sobreposição através de uma feição selecionada do Prisma."""

    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal(dict)

    def __init__(self, iface):
        """Método construtor da classe."""
        self.iface = iface
        super(OverlayFeature, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'overlay_feature.ui'), self)

        self.btn_voltar.clicked.connect(self.back)
        self.btn_continuar.clicked.connect(self.next)
        self.get_selected_features()

    def back(self):
        """
        Retorna para tela anterior.
        """
        self.hide()
        self.back_window.emit()

    def next(self):
        """
        Faz operações necessárias para iniciar o processo de busca de sobreposição através de uma feição selecionada.
        """
        data = self.get_selected_features()
        self.hide()
        self.continue_window.emit(data)

    def get_selected_features(self):
        """
        Extrai informações sobre as feições selecionadas como input para teste de sobreposição.

        @return data: Dados das feições selecionadas.
        """
        layer = self.iface.activeLayer()
        selected_features = layer.selectedFeatures()

        input = gpd.GeoDataFrame.from_features(selected_features, crs = iface.activeLayer().sourceCrs().authid())

        if 'cpf_cnpj' and 'logradouro' in input:
            self.hide()
            data = {"operation": "feature", "input": input}

            # Caso usuário tenha inserido área de aproximação
            if self.txt_aproximacao.text() != '' and float(self.txt_aproximacao.text()) > 0:
                data['aproximacao'] = float(self.txt_aproximacao.text())

            return data