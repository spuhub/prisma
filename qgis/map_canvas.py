# -*- coding: utf-8 -*-
from qgis.PyQt.QtWidgets import QApplication
from qgis.core import QgsProject, QgsVectorLayer, QgsFillSymbol, QgsLineSymbol, QgsMarkerSymbol, QgsRasterLayer, QgsCoordinateReferenceSystem
from qgis.utils import iface

import geopandas as gpd
import pandas as pd
from urllib.parse import quote

from ..utils.utils import Utils

class MapCanvas():
    """
    Classe responsável por gerenciar o mostrador do QGIS. Utilizada somente para os dois botões presentes na tela de resultados do PRISMA.
    Botões para mostrar todas as camadas comparadas e mostrar somente camadas sobrepostas.
    """
    def __init__(self):
        """Método construtor da classe."""
        self.data = None
        self.utils = Utils()
        self.basemap_name, self.basemap_link = self.utils.get_active_basemap()


    def print_all_layers_qgis(self, data):
        """
        Função que printa no QGIS todas as camadas que estão sendo comparadas.

        @keyword data: Dicionário que armazena configurações de operação, como por exemplo: dado de input, bases de dados selecionadas para comparação, busca por ponto, shapefile, etc...
        """
        self.data = data
        input = data['layers']['input']
        input_buffer = data['layers']['input_buffer'] if 'input_buffer' in data['layers'] else None
        lyr_overlap_point = data['layers']['lyr_overlap_point'] if 'lyr_overlap_point' in data['layers'] else None
        lyr_overlap_line = data['layers']['lyr_overlap_line'] if 'lyr_overlap_line' in data['layers'] else None
        lyr_overlap_polygon = data['layers']['lyr_overlap_polygon'] if 'lyr_overlap_polygon' in data['layers'] else None
        lyr_vertices = data['layers']['lyr_vertices'] if 'lyr_vertices' in data['layers'] else None

        list_selected_shp = data['layers']['shp']
        list_selected_wfs = data['layers']['wfs']
        list_selected_db = data['layers']['db']
        list_selected_required = data['layers']['required']

        lista_layers = []
        if input_buffer:
            lista_layers = [input_buffer]
            lista_layers += [input]
        else:
            lista_layers = [input]
        lista_layers += list_selected_required + list_selected_db + list_selected_shp + list_selected_wfs

        if lyr_overlap_point:
            lista_layers += [lyr_overlap_point]
        if lyr_overlap_line:
            lista_layers += [lyr_overlap_line]
        if lyr_overlap_polygon:
            lista_layers += [lyr_overlap_polygon]
        if lyr_vertices:
            lista_layers += [lyr_vertices]

        if 'basemap' in data['operation_config']:
            layer = QgsRasterLayer(self.basemap_link, self.basemap_name, 'wms')
        else:
            # Carrega camada mundial do OpenStreetMap
            tms = 'type=xyz&url=http://a.tile.openstreetmap.org/{z}/{x}/{y}.png'
            layer = QgsRasterLayer(tms, 'OpenStreetMap', 'wms')

        QgsProject.instance().addMapLayer(layer)
        QgsProject.instance().setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
        QApplication.instance().processEvents()

        for layer in lista_layers:
            QgsProject.instance().addMapLayer(layer.clone())
        
        # Repaint the canvas map
        iface.mapCanvas().refresh()
        # Da zoom na camada de input
        iface.zoomToActiveLayer()

    def print_overlay_qgis(self, data):
        """
        Função que printa no QGIS todas as camadas que apresentaram sobreposição entre camada de input e camadas selecionadas para comparação.

        @keyword data: Dicionário que armazena configurações de operação, como por exemplo: dado de input, bases de dados selecionadas para comparação, busca por ponto, shapefile, etc...
        """
        self.data = data
        input = data['layers']['input']
        input_buffer = data['layers']['input_buffer'] if 'input_buffer' in data['layers'] else None
        lyr_overlap_point = data['layers']['lyr_overlap_point'] if 'lyr_overlap_point' in data['layers'] else None
        lyr_overlap_line = data['layers']['lyr_overlap_line'] if 'lyr_overlap_line' in data['layers'] else None
        lyr_overlap_polygon = data['layers']['lyr_overlap_polygon'] if 'lyr_overlap_polygon' in data['layers'] else None
        lyr_vertices = data['layers']['lyr_vertices'] if 'lyr_vertices' in data['layers'] else None
        list_overlaps = data['overlaps']
        list_overlaps = [list_overlaps[item][0] for item in list_overlaps]

        if input_buffer:
            lista_layers = [input_buffer]
            lista_layers += [input]
        else:
            lista_layers = [input]
        if lyr_overlap_point:
            lista_layers += [lyr_overlap_point]
        if lyr_overlap_line:
            lista_layers += [lyr_overlap_line]
        if lyr_overlap_polygon:
            lista_layers += [lyr_overlap_polygon]
        if lyr_vertices:
            lista_layers += [lyr_vertices]
        lista_layers += list_overlaps

        if 'basemap' in data['operation_config']:
            layer = QgsRasterLayer(self.basemap_link, self.basemap_name, 'wms')
        else:
            # Carrega camada mundial do OpenStreetMap
            tms = 'type=xyz&url=http://a.tile.openstreetmap.org/{z}/{x}/{y}.png'
            layer = QgsRasterLayer(tms, 'OpenStreetMap', 'wms')

        QgsProject.instance().addMapLayer(layer)
        QgsProject.instance().setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
        QApplication.instance().processEvents()

        for layer in lista_layers:
            QgsProject.instance().addMapLayer(layer.clone())

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

    def get_input_symbol(self, geometry_type, show_qgis_input):
        """
        Estilização dinâmica para diferentes tipos de geometrias (Área de input).

        @keyword geometry_type: Tipo de geometria da área de input (com ou se buffer de área de aproximação).
        @return symbol: Retorna o objeto contendo a estilização de uma determinada camada.
        """
        symbol = None

        # Point
        if geometry_type == 0:
            show_qgis_input.loadSldStyle(
                self.data['data']['sld_default_layers']['default_input_point'])
        # Line String
        if geometry_type == 1:
            show_qgis_input.loadSldStyle(
                self.data['data']['sld_default_layers']['default_input_line'])
        # Polígono
        elif geometry_type == 2:
            show_qgis_input.loadSldStyle(
                self.data['data']['sld_default_layers']['default_input_polygon'])

    def get_input_standard_symbol(self, geometry_type, show_qgis_input):
        """
        Estilização dinâmica para diferentes tipos de geometrias (Área de input sem o buffer de aproximação).

        @keyword geometry_type: Tipo de geometria da área de input sem o buffer de aproximação.
        @return symbol: Retorna o objeto contendo a estilização de uma determinada camada.
        """
        symbol = None

        # Point
        if geometry_type == 0:
            show_qgis_input.loadSldStyle(
                self.data['data']['sld_default_layers']['default_input_point'])
        # Line String
        if geometry_type == 1:
            show_qgis_input.loadSldStyle(
                self.data['data']['sld_default_layers']['default_input_line'])
        # Polígono
        elif geometry_type == 2:
            show_qgis_input.loadSldStyle(
                self.data['data']['sld_default_layers']['default_input_polygon'])

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