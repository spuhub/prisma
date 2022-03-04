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

    def __init__(self, result):
        """
        Método para inicialização da classe.
        """
        self.result = result
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
        input = self.result['input']

        layers_bd = 0
        for i in self.result['operation_config']['pg']:
            layers_bd += len(i['tabelasCamadas'])

        # Seta label contendo quantidade de feições da camada de input
        self.label_feicoes_input.setText("A camada de input possui " + str(len(input)) + " feições")

        # Configura quantidade de linhas e as colunas da tabela de resultados
        self.tbl_result.setColumnCount(2)
        self.tbl_result.setRowCount(len(self.result['operation_config']['shp']) + len(self.result['operation_config']['pg']) + len(self.result['operation_config']['required']))
        self.tbl_result.setHorizontalHeaderLabels(['Camada', 'Sobreposições'])

        self.tbl_result.horizontalHeader().setStretchLastSection(True)
        self.tbl_result.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.overlay_counter_shp()
        self.overlay_counter_pg()
        self.overlay_counter_required()


    def overlay_counter_shp(self):
        """
        Faz a contagem de quantas sobreposições aconteceram com as áreas de shapefile selecionadas
        e realiza a inserção deste valor na tabela.
        """
        gdf_result_shp = gpd.GeoDataFrame.from_dict(self.result['overlay_shp'])

        for i in self.result['operation_config']['shp']:
            cont = 0
            for rowIndex, row in gdf_result_shp.iterrows():
                if str(i['nomeFantasiaCamada']) in gdf_result_shp and row[str(i['nomeFantasiaCamada'])] == True:
                    cont += 1

            cellName = QtWidgets.QTableWidgetItem(str(i['nome']))
            self.tbl_result.setItem(self.row_control, 0, cellName)

            cellValue = QtWidgets.QTableWidgetItem(str(cont))
            self.tbl_result.setItem(self.row_control, 1, cellValue)

            self.row_control += 1


    def overlay_counter_pg(self):
        """
        Faz a contagem de quantas sobreposições aconteceram com as áreas de banco de dados selecionados
        e realiza a inserção deste valor na tabela
        """
        gdf_result_db = gpd.GeoDataFrame.from_dict(self.result['overlay_db'])

        for bd in self.result['operation_config']['pg']:
            cont = 0
            for layer in bd['nomeFantasiaTabelasCamadas']:
                for rowIndex, row in gdf_result_db.iterrows():
                    if str(str(layer)) in gdf_result_db and row[str(layer)] == True:
                        cont += 1

                cellName = QtWidgets.QTableWidgetItem(str(layer))
                self.tbl_result.setItem(self.row_control, 0, cellName)

                cellValue = QtWidgets.QTableWidgetItem(str(cont))
                self.tbl_result.setItem(self.row_control, 1, cellValue)

                self.row_control += 1

    def overlay_counter_required(self):
        """
        Faz a contagem de quantas sobreposições aconteceram com as áreas de shapefile selecionadas
        e realiza a inserção deste valor na tabela.
        """
        gdf_result_shp = gpd.GeoDataFrame.from_dict(self.result['overlay_required'])
        for i in self.result['operation_config']['required']:
            cont = 0

            for rowIndex, row in gdf_result_shp.iterrows():
                if i['tipo'] == 'shp':
                    if str(i['nomeFantasiaCamada'][0]) in gdf_result_shp and row[str(i['nomeFantasiaCamada'][0])] == True:
                        cont += 1
                else:
                    if str(i['nomeFantasiaTabelasCamadas'][0]) in gdf_result_shp and row[str(i['nomeFantasiaTabelasCamadas'][0])] == True:
                        cont += 1

            if 'nomeFantasiaCamada' in i:
                cellName = QtWidgets.QTableWidgetItem(str(i['nomeFantasiaCamada'][0]))
            else:
                cellName = QtWidgets.QTableWidgetItem(str(i['nomeFantasiaTabelasCamadas'][0]))

            self.tbl_result.setItem(self.row_control, 0, cellName)
            cellValue = QtWidgets.QTableWidgetItem(str(cont))
            self.tbl_result.setItem(self.row_control, 1, cellValue)

            self.row_control += 1

    def print_overlay_qgis(self):
        """
        Exibe no mostrador do QGIS somente feições que tiveram sobreposição.
        """
        mc = MapCanvas()
        mc.print_overlay_qgis(self.result)

    def print_all_layers_qgis(self):
        """
        Exibe no mostrador do QGIS todas as feições das camadas comparadas.
        """
        mc = MapCanvas()
        mc.print_all_layers_qgis(self.result)

    def btn_report_generator(self):
        """
        Função acionada quando o usuário pressiona o botão para gerar relatórios PDF.
        """
        self.hide()
        self.report_generator_window.emit(self.result)