import sys
import os.path

from qgis.PyQt.QtWidgets import QAction, QFileDialog

from qgis.core import QgsProject, QgsVectorLayer, QgsFillSymbol

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

from ..settings.jsonTools import JsonTools

import geopandas as gpd

class ResultWindow (QtWidgets.QDialog):
    cancel_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self, result):
        self.result = result
        super(ResultWindow, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'result_window.ui'), self)

        self.btn_output.clicked.connect(self.handle_output)
        self.btn_cancel.clicked.connect(self.cancel)
        self.btn_continuar.clicked.connect(self.next)

        self.show_result()

    # Exibe em uma lista a quantidade de sobreposições que se teve com determinada área
    def show_result(self):
        if(self.result['operation'] == 'shapefile'):
            gdf_result_shp = gpd.GeoDataFrame.from_dict(self.result['gdf_shp'])
            gdf_result_pg = gpd.GeoDataFrame.from_dict(self.result['gdf_pg'])

            show_result_shp = gdf_result_shp.query('sobreposicao == True').reset_index()
            show_result_pg = gdf_result_pg.query('sobreposicao == True').reset_index()

            layers_bd = 0
            for i in self.result['operation_data']['pg']:
                layers_bd += len(i['tabelasCamadas'])

            # Configura quantidade de linhas e as colunas da tabela de resultados
            self.tbl_result.setColumnCount(2)
            self.tbl_result.setRowCount(len(self.result['operation_data']['shp']) + layers_bd)
            self.tbl_result.setHorizontalHeaderLabels(['Camada', 'Sobreposições'])

            self.tbl_result.horizontalHeader().setStretchLastSection(True)
            self.tbl_result.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

            row_control = 0
            # Faz a contagem de quantas sobreposições aconteceram com as áreas de shapefile selecionadas
            # e realiza a inserção deste valor na tabela
            for i in self.result['operation_data']['shp']:
                cont = 0
                for rowIndex, row in show_result_shp.iterrows():
                    if str(i['nome']) in show_result_shp and row[str(i['nome'])] > 0:
                        cont += 1

                cellName = QtWidgets.QTableWidgetItem(str(i['nome']))
                self.tbl_result.setItem(row_control, 0, cellName)

                cellValue = QtWidgets.QTableWidgetItem(str(cont))
                self.tbl_result.setItem(row_control, 1, cellValue)

                row_control += 1

            # Faz a contagem de quantas sobreposições aconteceram com as áreas de banco de dados selecionados
            # e realiza a inserção deste valor na tabela
            for bd in self.result['operation_data']['pg']:
                cont = 0
                for layer in bd['nomeFantasiaTabelasCamadas']:
                    for rowIndex, row in show_result_pg.iterrows():
                        if str(layer) in show_result_pg and row[str(layer)] > 0:
                            cont += 1

                    cellName = QtWidgets.QTableWidgetItem(str(layer))
                    self.tbl_result.setItem(row_control, 0, cellName)

                    cellValue = QtWidgets.QTableWidgetItem(str(cont))
                    self.tbl_result.setItem(row_control, 1, cellValue)

                    row_control += 1


            # if (len(show_result_shp) > 0):
            #     self.tbl_result.setColumnCount(len(show_result_shp.columns))
            #     self.tbl_result.setRowCount(len(show_result_shp))
            #
            #     header_labels = show_result_shp.columns
            #
                # self.tbl_result.setHorizontalHeaderLabels(header_labels)
                # for rowIndex, row in show_result_shp.iterrows():  # iterando sobre linhas
                #     columnIndex = 0
                #     for columnName, value in row.items():   # iterando sobre colunas
                #             cell = QtWidgets.QTableWidgetItem(str(value))
                #             self.tbl_result.setItem(rowIndex, columnIndex, cell)
                #             columnIndex += 1
            #
            # if (len(show_result_pg) > 0):
            #     self.tbl_result.setColumnCount(len(show_result_pg.columns))
            #     self.tbl_result.setRowCount(len(show_result_pg))
            #
            #     header_labels = show_result_pg.columns
            #
            #     self.tbl_result.setHorizontalHeaderLabels(header_labels)
            #     for rowIndex, row in show_result_pg.iterrows():  # iterando sobre linhas
            #         columnIndex = 0
            #         for columnName, value in row.items():  # iterando sobre colunas
            #             cell = QtWidgets.QTableWidgetItem(str(value))
            #             self.tbl_result.setItem(rowIndex, columnIndex, cell)
            #             columnIndex += 1

    def handle_output(self):
        self.output = QFileDialog.getExistingDirectory(self, "Selecione a pasta de saída")
        self.txt_output.setText(self.output)

    def print_overlay_qgis(self):
        input = gpd.GeoDataFrame.from_dict(self.result['input'])
        areas_shp = []
        areas_db = []

        for i in range(len(self.result['areas_shp'])):
            areas_shp.append(gpd.GeoDataFrame.from_dict(self.result['areas_shp'][i]))

        for i in range(len(self.result['areas_db'])):
            areas_db.append(gpd.GeoDataFrame.from_dict(self.result['areas_db'][i]))

        # Exibe de sobreposição entre input e Shapefiles
        index = -1
        index_show_overlay = 0
        gdf_input = gpd.GeoDataFrame(columns = input.columns)
        print_input = False
        for area in areas_shp:
            index += 1
            gdf_area = gpd.GeoDataFrame(columns = area.columns)
            for indexArea, rowArea in area.iterrows():
                for indexInput, rowInput in input.iterrows():
                    if (rowArea['geometry'].intersection(rowInput['geometry'])):
                        gdf_input.loc[index_show_overlay] = rowInput
                        gdf_area.loc[index_show_overlay] = rowArea
                        index_show_overlay += 1

            if len(gdf_area) > 0:
                print_input = True

                gdf_area = gdf_area.drop_duplicates()
                show_qgis_areas = QgsVectorLayer(gdf_area.to_json(), self.result['operation_data']['shp'][index]['nomeFantasiaCamada'])

                symbol = QgsFillSymbol.createSimple(self.result['operation_data']['shp'][index]['estiloCamadas'][0])
                show_qgis_areas.renderer().setSymbol(symbol)
                QgsProject.instance().addMapLayer(show_qgis_areas)

        # Exibe de sobreposição entre input e Postgis
        index = -1
        for area in areas_db:
            index += 1
            gdf_area = gpd.GeoDataFrame(columns=area.columns)
            for indexArea, rowArea in area.iterrows():
                for indexInput, rowInput in input.iterrows():
                    if (rowArea['geometry'].intersection(rowInput['geometry'])):
                        gdf_input.loc[index_show_overlay] = rowInput
                        gdf_area.loc[index_show_overlay] = rowArea
                        index_show_overlay += 1

            if len(gdf_area) > 0:
                print_input = True
                print(self.result['operation_data']['pg'][index])
                #                                      'nomeFantasiaCamada'])

                #
                # gdf_area = gdf_area.drop_duplicates()
                # show_qgis_areas = QgsVectorLayer(gdf_area.to_json(),
                #                                  self.result['operation_data']['shp'][index][
                #                                      'nomeFantasiaCamada'])
                #
                # symbol = QgsFillSymbol.createSimple(
                #     self.result['operation_data']['shp'][index]['estiloCamadas'][0])
                # show_qgis_areas.renderer().setSymbol(symbol)
                # QgsProject.instance().addMapLayer(show_qgis_areas)


        if print_input:
            gdf_input = gdf_input.drop_duplicates()

            show_qgis_input = QgsVectorLayer(gdf_input.to_json(), "input")
            QgsProject.instance().addMapLayer(show_qgis_input)



    def cancel(self):
        self.hide()
        self.cancel_window.emit()

    def next(self):
        self.hide()

        # Verifica se o usuário deseja exibir as camadas de sobreposição no mostrador do Qgis
        if self.check_camadas.isChecked():
            self.print_overlay_qgis()

            # Exibe a camada de input que possui sobreposição
            # show_qgis_input = QgsVectorLayer(input.to_json(), "input")
            # QgsProject.instance().addMapLayer(show_qgis_input)
            #
            # # Exibe camadas de shapefile que foram selecionadas para comparação
            # show_qgis_area = QgsVectorLayer(gdf_result_shp.to_json(), "militar")
            # QgsProject.instance().addMapLayer(show_qgis_area)
            #
            # # Exibe camadas de banco de dados que foram selecionadas para comparação
            # show_qgis_area = QgsVectorLayer(gdf_result_pg.to_json(), "teste")
            # QgsProject.instance().addMapLayer(show_qgis_area)

        self.continue_window.emit()