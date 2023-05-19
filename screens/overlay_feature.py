import sys
import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

from qgis.core import QgsFeature, QgsVectorLayer

class OverlayFeature(QtWidgets.QDialog):
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

    def back(self):
        """
        Retorna para tela anterior.
        """
        self.hide()

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

        input_features = []
        for feature in selected_features:
            geom = feature.geometry()
            if not geom:
                continue
            input_feature = QgsFeature()
            input_feature.setGeometry(geom)
            input_feature.setFields(feature.fields())  # Define os campos da nova QgsFeature com base na QgsFeature original
            input_feature.setAttributes(feature.attributes())  # Define os atributos da nova QgsFeature com base na QgsFeature original
            input_features.append(input_feature)

        if not input_features:
            self.iface.messageBar().pushMessage("Erro", "Selecione uma feição de entrada.", level=1)
            return

        # Cria um novo layer temporário a partir das feições selecionadas
        input_layer = QgsVectorLayer("Polygon", "input_layer", "memory", crs=layer.crs())
        input_layer.startEditing()
        input_layer.dataProvider().addAttributes(input_features[0].fields())  # Adiciona os campos do primeiro feature da lista
        input_layer.updateFields()  # Atualiza os campos do novo layer
        input_layer.dataProvider().addFeatures(input_features)  # Adiciona as features ao novo layer
        input_layer.commitChanges()  # Salva as alterações


        self.hide()
        data = {"operation": "feature", "input": {"layer": input_layer}}

        # Caso usuário tenha inserido área de aproximação
        if self.txt_aproximacao.text() != '' and float(self.txt_aproximacao.text()) > 0:
            data['input'].update(aproximacao = float(self.txt_aproximacao.text()))

        return data