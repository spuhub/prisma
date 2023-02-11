import os.path

from ..qgis.map_canvas import MapCanvas

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

import geopandas as gpd

class ResultWindow (QtWidgets.QDialog):
    """
    Classe responsável por fazer o backend da tela de resultados, que exibe a quatidade de sobreposição que aconteceu entre a camada de input e camadas de comparação; Da ao usuário opção para
    mostrar as camadas no mostrador do QGIS e também gerar os relatórios PDF.

    """
    cancel_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()
    report_generator_window = QtCore.pyqtSignal(dict)

    def __init__(self, data):
        """
        Método para inicialização da classe.
        """
        self.data = data
        self.row_control = 0
        super(ResultWindow, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'result_window.ui'), self)

        self.progress_bar.setHidden(True)

        self.btn_print_overlay_qgis.clicked.connect(self.print_overlay_qgis)
        self.btn_print_all_layers_qgis.clicked.connect(self.print_all_layers_qgis)
        self.btn_pdf_generator.clicked.connect(self.btn_report_generator)

        self.show_result()

    def show_result(self):
        """
        Exibe em uma lista a quantidade de sobreposições que se teve com determinada área
        """
        lyr_input = self.data['layers']['input']
        lyr_input.selectAll()

        dic_overlaps = self.data['overlaps']

        # Seta label contendo quantidade de feições da camada de input
        self.label_feicoes_input.setText(f"A camada de input possui {lyr_input.selectedFeatureCount()} feições")

        # Configura quantidade de linhas e as colunas da tabela de resultados
        self.tbl_result.setColumnCount(2)
        self.tbl_result.setRowCount(len(list(self.data['overlaps'].keys())))
        self.tbl_result.setHorizontalHeaderLabels(['Camada', 'Sobreposições'])

        self.tbl_result.horizontalHeader().setStretchLastSection(True)
        self.tbl_result.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        for idx, lyrName in enumerate(dic_overlaps):
            cellLyrName = QtWidgets.QTableWidgetItem(lyrName)
            self.tbl_result.setItem(idx, 0, cellLyrName)

            cellLyrOverlaps = QtWidgets.QTableWidgetItem(str(dic_overlaps[lyrName]))
            self.tbl_result.setItem(idx, 1, cellLyrOverlaps)


    def print_overlay_qgis(self):
        """
        Exibe no mostrador do QGIS somente feições que tiveram sobreposição.
        """
        mc = MapCanvas()
        mc.print_overlay_qgis(self.data)

    def print_all_layers_qgis(self):
        """
        Exibe no mostrador do QGIS todas as feições das camadas comparadas.
        """
        mc = MapCanvas()
        mc.print_all_layers_qgis(self.data)

    def btn_report_generator(self):
        """
        Função acionada quando o usuário pressiona o botão para gerar relatórios PDF.
        """
        self.report_generator_window.emit(self.data)