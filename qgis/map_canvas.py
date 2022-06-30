# -*- coding: utf-8 -*-
from qgis.PyQt.QtWidgets import QApplication
from qgis.core import QgsProject, QgsVectorLayer, QgsFillSymbol, QgsLineSymbol, QgsMarkerSymbol, QgsRasterLayer, QgsCoordinateReferenceSystem
from qgis.utils import iface

import geopandas as gpd
import pandas as pd

class MapCanvas():
    """
    Classe responsável por gerenciar o mostrador do QGIS. Utilizada somente para os dois botões presentes na tela de resultados do PRISMA.
    Botões para mostrar todas as camadas comparadas e mostrar somente camadas sobrepostas.
    """
    def __init__(self):
        """Método construtor da classe."""
        pass


    def print_all_layers_qgis(self, operation_config):
        """
        Função que printa no QGIS todas as camadas que estão sendo comparadas.

        @keyword operation_config: Dicionário que armazena configurações de operação, como por exemplo: dado de input, bases de dados selecionadas para comparação, busca por ponto, shapefile, etc...
        """
        input = operation_config['input']
        input_standard = operation_config['input_standard']

        gdf_selected_shp = operation_config['gdf_selected_shp']
        gdf_selected_db = operation_config['gdf_selected_db']

        # Carrega camada mundial do OpenStreetMap
        tms = 'type=xyz&url=http://a.tile.openstreetmap.org/{z}/{x}/{y}.png'
        layer = QgsRasterLayer(tms, 'OpenStreetMap', 'wms')

        QgsProject.instance().addMapLayer(layer)
        QApplication.instance().processEvents()
        QgsProject.instance().setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))

        # Carrega camadas shapefiles
        index = -1
        index_show_overlay = 0
        input = input.to_crs(epsg='4326')
        for area in gdf_selected_shp:
            area = area.to_crs(epsg='4326')
            index += 1

            if len(area) > 0:
                show_qgis_areas = QgsVectorLayer(area.to_json(), operation_config['operation_config']['shp'][index]['nomeFantasiaCamada'])
                show_qgis_areas.loadSldStyle(operation_config['operation_config']['shp'][index]['estiloCamadas'][0]['stylePath'])
                QgsProject.instance().addMapLayer(show_qgis_areas)

        # Exibe de sobreposição entre input e Postgis
        index_db = 0
        for db in gdf_selected_db:
            index_layer = 0
            for area in db:
                if 'geom' in area:
                    area = area.drop(columns=['geom'])

                if len(area) > 0:
                    show_qgis_areas = QgsVectorLayer(area.to_json(),
                                                     operation_config['operation_config']['pg'][index_db][
                                                         'nomeFantasiaTabelasCamadas'][index_layer])
                    show_qgis_areas.loadSldStyle(
                        operation_config['operation_config']['pg'][index_db]['estiloTabelasCamadas'][index_layer]['stylePath'])
                    QgsProject.instance().addMapLayer(show_qgis_areas)
                index_layer += 1
            index_db += 1

        if 'aproximacao' in operation_config['operation_config']:
            show_qgis_input = QgsVectorLayer(input.to_json(), "Feição de Estudo/Sobreposição")

            symbol = self.get_input_symbol(show_qgis_input.geometryType())
            show_qgis_input.renderer().setSymbol(symbol)

            QgsProject.instance().addMapLayer(show_qgis_input)

            show_qgis_input_standard = QgsVectorLayer(input_standard.to_json(), "Feição de Estudo/Sobreposição (padrão)")

            symbol = self.get_input_standard_symbol(show_qgis_input_standard.geometryType())
            show_qgis_input_standard.renderer().setSymbol(symbol)

            QgsProject.instance().addMapLayer(show_qgis_input_standard)
        else:
            show_qgis_input = QgsVectorLayer(input.to_json(), "Feição de Estudo/Sobreposição")

            symbol = self.get_input_standard_symbol(show_qgis_input.geometryType())
            show_qgis_input.renderer().setSymbol(symbol)

            QgsProject.instance().addMapLayer(show_qgis_input)

        # Repaint the canvas map
        iface.mapCanvas().refresh()
        # Da zoom na camada de input
        iface.zoomToActiveLayer()

    def print_overlay_qgis(self, operation_config):
        """
        Função que printa no QGIS todas as camadas que apresentaram sobreposição entre camada de input e camadas selecionadas para comparação.

        @keyword operation_config: Dicionário que armazena configurações de operação, como por exemplo: dado de input, bases de dados selecionadas para comparação, busca por ponto, shapefile, etc...
        """
        input = operation_config['input']
        input_standard = operation_config['input_standard']

        gdf_selected_shp = operation_config['gdf_selected_shp']
        gdf_selected_db = operation_config['gdf_selected_db']

        # Carrega camada mundial do OpenStreetMap
        tms = 'type=xyz&url=http://a.tile.openstreetmap.org/{z}/{x}/{y}.png'
        layer = QgsRasterLayer(tms, 'OpenStreetMap', 'wms')

        QgsProject.instance().addMapLayer(layer)
        QApplication.instance().processEvents()
        QgsProject.instance().setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))

        # Exibe de sobreposição entre input e Shapefiles
        index = -1
        index_show_overlay = 0
        gdf_input = gpd.GeoDataFrame(columns = input.columns)
        print_input = False
        input = input.to_crs(epsg='4326')
        for area in gdf_selected_shp:
            area = area.to_crs(epsg='4326')
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
                show_qgis_areas = QgsVectorLayer(gdf_area.to_json(), operation_config['operation_config']['shp'][index]['nomeFantasiaCamada'])
                show_qgis_areas.loadSldStyle(
                    operation_config['operation_config']['shp'][index]['estiloCamadas'][0]['stylePath'])
                QgsProject.instance().addMapLayer(show_qgis_areas)

        # Exibe de sobreposição entre input e Postgis
        index_db = 0
        for db in gdf_selected_db:
            index_layer = 0
            for area in db:
                gdf_area = gpd.GeoDataFrame(columns=area.columns)
                for indexArea, rowArea in area.iterrows():
                    for indexInput, rowInput in input.iterrows():
                        if (rowArea['geometry'].intersection(rowInput['geometry'])):
                            gdf_input.loc[index_show_overlay] = rowInput
                            gdf_area.loc[index_show_overlay] = rowArea
                            index_show_overlay += 1

                if len(gdf_area) > 0:
                    print_input = True

                    if 'geom' in gdf_area:
                        gdf_area = gdf_area.drop(columns=['geom'])

                    gdf_area = gdf_area.drop_duplicates()

                    show_qgis_areas = QgsVectorLayer(gdf_area.to_json(),
                                                     operation_config['operation_config']['pg'][index_db][
                                                         'nomeFantasiaTabelasCamadas'][index_layer])
                    show_qgis_areas.loadSldStyle(
                        operation_config['operation_config']['pg'][index_db]['estiloTabelasCamadas'][index_layer][
                            'stylePath'])
                    QgsProject.instance().addMapLayer(show_qgis_areas)

                index_layer += 1
            index_db += 1

        if print_input:
            if 'aproximacao' in operation_config['operation_config']:
                gdf_input = gdf_input.drop_duplicates()

                show_qgis_input = QgsVectorLayer(gdf_input.to_json(), "Feição de Estudo/Sobreposição")

                symbol = self.get_input_symbol(show_qgis_input.geometryType())
                show_qgis_input.renderer().setSymbol(symbol)

                QgsProject.instance().addMapLayer(show_qgis_input)

                input_standard = input_standard.to_crs(4326)
                # gdf_input = gdf_input.to_crs(4326)
                get_overlay_standard = self.get_overlay_features(input, input_standard, gdf_selected_shp, gdf_selected_db)

                show_qgis_input_standard = QgsVectorLayer(get_overlay_standard.to_json(), "Feição de Estudo/Sobreposição (padrão)")

                symbol = self.get_input_standard_symbol(show_qgis_input_standard.geometryType())
                show_qgis_input_standard.renderer().setSymbol(symbol)

                QgsProject.instance().addMapLayer(show_qgis_input_standard)

            else:
                input_standard = input_standard.to_crs(4326)
                # gdf_input = gdf_input.to_crs(4326)
                get_overlay_standard = self.get_overlay_features(input, input_standard, gdf_selected_shp, gdf_selected_db)

                show_qgis_input_standard = QgsVectorLayer(get_overlay_standard.to_json(),
                                                          "Feição de Estudo/Sobreposição")

                symbol = self.get_input_standard_symbol(show_qgis_input_standard.geometryType())
                show_qgis_input_standard.renderer().setSymbol(symbol)

                QgsProject.instance().addMapLayer(show_qgis_input_standard)

            # Repaint the canvas map
            iface.mapCanvas().refresh()
            # Da zoom na camada de input
            iface.zoomToActiveLayer()

    def get_overlay_features(self, input, input_standard, gdf_selected_shp, gdf_selected_db):
        """
        Verifica, entre camada de input e camadas selecionadas para comparação, quais possuem sobreposição.

        @keyword input: Camada contendo feições de input.
        @keyword input_standard: Camada contendo feições de input, porém se o buffer de proximidade (caso necessário).
        @keyword gdf_selected_shp: Vetor de camadas shapefile selecionadas para comparação.
        @keyword gdf_selected_db: Vetor de camadas de banco de dados selecionados para comparação.
        """
        get_overlay_standard = gpd.GeoDataFrame(columns=input_standard.columns)

        # Teste com shapefile
        for area in gdf_selected_shp:
            for indexArea, rowArea in area.iterrows():
                for indexInput, rowInput in input.iterrows():
                    if rowInput['geometry'].intersection(rowArea['geometry']):
                        get_overlay_standard = gpd.GeoDataFrame(
                            pd.concat([get_overlay_standard, input_standard.iloc[[indexInput]]]))

        # Teste com banco de dados
        index_db = 0
        for db in gdf_selected_db:
            index_layer = 0
            for area in db:
                if 'geom' in area:
                    area = area.drop(columns=['geom'])

                for indexInput, rowInput in input.iterrows():
                    for indexArea, rowArea in area.iterrows():
                        if rowInput['geometry'].intersection(rowArea['geometry']):
                            get_overlay_standard = gpd.GeoDataFrame(
                                pd.concat([get_overlay_standard, input_standard.iloc[[indexInput]]]))
                index_layer += 1
            index_db += 1

        get_overlay_standard = get_overlay_standard.drop_duplicates()
        get_overlay_standard = get_overlay_standard.reset_index()

        return get_overlay_standard

    def get_input_symbol(self, geometry_type):
        """
        Estilização dinâmica para diferentes tipos de geometrias (Área de input).

        @keyword geometry_type: Tipo de geometria da área de input (com ou se buffer de área de aproximação).
        @return symbol: Retorna o objeto contendo a estilização de uma determinada camada.
        """
        symbol = None

        # Point
        if geometry_type == 0:
            symbol = QgsMarkerSymbol.createSimple({'name': 'dot', 'color': '#616161'})
        # Line String
        if geometry_type == 1:
            symbol = QgsLineSymbol.createSimple({"line_color": "#616161", "line_style": "solid", "width": "0.35"})
        # Polígono
        elif geometry_type == 2:
            symbol = QgsFillSymbol.createSimple(
                {'line_style': 'solid', 'line_color': 'black', 'color': '#616161', 'width_border': '0,35',
                 'style': 'solid'})

        return symbol

    def get_input_standard_symbol(self, geometry_type):
        """
        Estilização dinâmica para diferentes tipos de geometrias (Área de input sem o buffer de aproximação).

        @keyword geometry_type: Tipo de geometria da área de input sem o buffer de aproximação.
        @return symbol: Retorna o objeto contendo a estilização de uma determinada camada.
        """
        symbol = None

        # Point
        if geometry_type == 0:
            symbol = QgsMarkerSymbol.createSimple({'name': 'dot', 'color': 'gray'})
        # Line String
        if geometry_type == 1:
            symbol = QgsLineSymbol.createSimple({"line_color": "gray", "line_style": "solid", "width": "0.35"})
        # Polígono
        elif geometry_type == 2:
            symbol = QgsFillSymbol.createSimple({'line_style': 'solid', 'line_color': 'black', 'color': 'gray', 'width_border': '0,35', 'style': 'solid'})

        return symbol

    def get_feature_symbol(self, geometry_type, style):
        """
        Estilização dinâmica para diferentes tipos de geometrias (Áreas de comparação).

        @keyword geometry_type: Tipo de geometria da área de comparação.
        @keyword style: Variável armazena o estilo que será usado para a projeção de uma determinada camada. Este estilo é obtido através do arquivo JSON de configuração.
        @return symbol: Retorna o objeto contendo a estilização de uma determinada camada.
        """
        symbol = None

        # Point
        if geometry_type == 0 or geometry_type == 4:
            symbol = QgsMarkerSymbol.createSimple(style)
        # Line String
        elif geometry_type == 1 or geometry_type == 5:
            symbol = QgsLineSymbol.createSimple(style)
        # Polígono
        elif geometry_type == 2 or geometry_type == 6:
            symbol = QgsFillSymbol.createSimple(style)

        return symbol