import os.path

from qgis.PyQt.QtWidgets import QFileDialog
from ..qgis.layout_manager import LayoutManager
from ..qgis.map_canvas import MapCanvas

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

import geopandas as gpd

class ResultWindow (QtWidgets.QDialog):
    cancel_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self, result):
        self.result = result
        super(ResultWindow, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'result_window.ui'), self)

        self.btn_output.clicked.connect(self.handle_output)
        self.btn_print_overlay_qgis.clicked.connect(self.print_overlay_qgis)
        self.btn_cancel.clicked.connect(self.cancel)
        self.btn_continuar.clicked.connect(self.next)

        self.show_result()

    # Exibe em uma lista a quantidade de sobreposições que se teve com determinada área
    def show_result(self):
        if(self.result['operation_config']['operation'] == 'shapefile'):
            input = self.result['input']

            gdf_result_shp = gpd.GeoDataFrame.from_dict(self.result['overlay_shp'])
            gdf_result_db = gpd.GeoDataFrame.from_dict(self.result['overlay_db'])

            # show_result_shp = gdf_result_shp.query('sobreposicao == True').reset_index()
            # show_result_db = gdf_result_db.query('sobreposicao == True').reset_index()

            layers_bd = 0
            for i in self.result['operation_config']['pg']:
                layers_bd += len(i['tabelasCamadas'])

            # Configura quantidade de linhas e as colunas da tabela de resultados
            self.tbl_result.setColumnCount(3)
            self.tbl_result.setRowCount(len(self.result['operation_config']['shp']) + layers_bd)
            self.tbl_result.setHorizontalHeaderLabels(['Camada', 'Feições camada de input', 'Sobreposições'])

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

                cellName = QtWidgets.QTableWidgetItem(str(len(input)))
                self.tbl_result.setItem(row_control, 1, cellName)

                cellValue = QtWidgets.QTableWidgetItem(str(cont))
                self.tbl_result.setItem(row_control, 2, cellValue)

                row_control += 1

            # Faz a contagem de quantas sobreposições aconteceram com as áreas de banco de dados selecionados
            # e realiza a inserção deste valor na tabela
            for bd in self.result['operation_config']['pg']:
                cont = 0
                for layer in bd['nomeFantasiaTabelasCamadas']:
                    for rowIndex, row in gdf_result_db.iterrows():
                        if row[str(layer)]:
                            cont += 1

                        # if str(layer) in gdf_result_db and row[str(layer)] > 0:
                        #     cont += 1

                    cellName = QtWidgets.QTableWidgetItem(str(layer))
                    self.tbl_result.setItem(row_control, 0, cellName)

                    cellName = QtWidgets.QTableWidgetItem(str(len(input)))
                    self.tbl_result.setItem(row_control, 1, cellName)

                    cellValue = QtWidgets.QTableWidgetItem(str(cont))
                    self.tbl_result.setItem(row_control, 2, cellValue)

                    row_control += 1

    def handle_output(self):
        self.output = QFileDialog.getExistingDirectory(self, "Selecione a pasta de saída")
        self.txt_output.setText(self.output)

    def print_overlay_qgis(self):
        mc = MapCanvas()
        mc.print_overlay_qgis(self.result)

    def cancel(self):
        self.hide()
        self.cancel_window.emit()

    def next(self):
        LayoutManager()

        self.hide()
        self.continue_window.emit()