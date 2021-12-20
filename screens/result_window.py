import os.path

from qgis.PyQt.QtWidgets import QFileDialog
from PyQt5.QtCore import QObject

from ..qgis.layout_manager import LayoutManager
from ..qgis.map_canvas import MapCanvas

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

import geopandas as gpd

class ResultWindow (QtWidgets.QDialog):
    cancel_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()
    report_generator_window = QtCore.pyqtSignal(dict)

    def __init__(self, result):
        self.result = result
        super(ResultWindow, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'result_window.ui'), self)

        self.progress_bar.setHidden(True)

        # self.btn_output.clicked.connect(self.handle_output)
        self.btn_print_overlay_qgis.clicked.connect(self.print_overlay_qgis)
        self.btn_print_all_layers_qgis.clicked.connect(self.print_all_layers_qgis)
        self.btn_pdf_generator.clicked.connect(self.btn_report_generator)
        self.btn_cancel.clicked.connect(self.cancel)
        self.btn_continuar.clicked.connect(self.next)

        self.show_result()

    # Exibe em uma lista a quantidade de sobreposições que se teve com determinada área
    def show_result(self):
        input = self.result['input']

        gdf_result_shp = gpd.GeoDataFrame.from_dict(self.result['overlay_shp'])
        gdf_result_db = gpd.GeoDataFrame.from_dict(self.result['overlay_db'])

        layers_bd = 0
        for i in self.result['operation_config']['pg']:
            layers_bd += len(i['tabelasCamadas'])

        # Seta label contendo quantidade de feições da camada de input
        self.label_feicoes_input.setText("A camada de input possui " + str(len(input)) + " feições")

        # Configura quantidade de linhas e as colunas da tabela de resultados
        self.tbl_result.setColumnCount(2)
        self.tbl_result.setRowCount(len(self.result['operation_config']['shp']) + layers_bd)
        self.tbl_result.setHorizontalHeaderLabels(['Camada', 'Sobreposições'])

        self.tbl_result.horizontalHeader().setStretchLastSection(True)
        self.tbl_result.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        row_control = 0
        # Faz a contagem de quantas sobreposições aconteceram com as áreas de shapefile selecionadas
        # e realiza a inserção deste valor na tabela
        for i in self.result['operation_config']['shp']:
            cont = 0
            for rowIndex, row in gdf_result_shp.iterrows():
                if str(i['nome']) in gdf_result_shp and row[str(i['nome'])] == True:
                    cont += 1

            cellName = QtWidgets.QTableWidgetItem(str(i['nome']))
            self.tbl_result.setItem(row_control, 0, cellName)

            cellValue = QtWidgets.QTableWidgetItem(str(cont))
            self.tbl_result.setItem(row_control, 1, cellValue)

            row_control += 1

            # Faz a contagem de quantas sobreposições aconteceram com as áreas de banco de dados selecionados
            # e realiza a inserção deste valor na tabela
            for bd in self.result['operation_config']['pg']:
                cont = 0
                for layer in bd['nomeFantasiaTabelasCamadas']:
                    for rowIndex, row in gdf_result_db.iterrows():
                        if row[str(layer)]:
                            cont += 1

                    cellName = QtWidgets.QTableWidgetItem(str(layer))
                    self.tbl_result.setItem(row_control, 0, cellName)

                    cellValue = QtWidgets.QTableWidgetItem(str(cont))
                    self.tbl_result.setItem(row_control, 1, cellValue)

                    row_control += 1

    def handle_output(self):
        self.output = QFileDialog.getExistingDirectory(self, "Selecione a pasta de saída")
        self.txt_output.setText(self.output)

    def print_overlay_qgis(self):
        mc = MapCanvas()
        mc.print_overlay_qgis(self.result)

    def print_all_layers_qgis(self):
        mc = MapCanvas()
        mc.print_all_layers_qgis(self.result)

    def btn_report_generator(self):
        self.hide()
        self.report_generator_window.emit(self.result)

    def cancel(self):
        self.hide()
        self.cancel_window.emit()

    def next(self):
        lm = LayoutManager(self.result, self.progress_bar)
        lm.export_pdf()

        self.hide()
        self.continue_window.emit()