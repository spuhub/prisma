from qgis.PyQt.QtWidgets import QApplication
from qgis.core import QgsProject, QgsVectorLayer, QgsFillSymbol, QgsLineSymbol, QgsMarkerSymbol, QgsRasterLayer, QgsCoordinateReferenceSystem
from qgis.utils import iface

import geopandas as gpd
import pandas as pd

class MapCanvas():
    def __init__(self):
        pass

    def print_all_layers_qgis(self, result):
        input = result['input']
        input_standard = result['input_standard']

        gdf_selected_shp = result['gdf_selected_shp']
        gdf_selected_db = result['gdf_selected_db']

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

            show_qgis_areas = QgsVectorLayer(area.to_json(), result['operation_config']['shp'][index]['nomeFantasiaCamada'])
            symbol = self.get_feature_symbol(show_qgis_areas.geometryType(), result['operation_config']['shp'][index]['estiloCamadas'][0])
            show_qgis_areas.renderer().setSymbol(symbol)
            QgsProject.instance().addMapLayer(show_qgis_areas)

        # Exibe de sobreposição entre input e Postgis
        index_db = 0
        for db in gdf_selected_db:
            index_layer = 0
            for area in db:
                if 'geom' in area:
                    area = area.drop(columns=['geom'])

                show_qgis_areas = QgsVectorLayer(area.to_json(),
                                                 result['operation_config']['pg'][index_db][
                                                     'nomeFantasiaTabelasCamadas'][index_layer])
                symbol = self.get_feature_symbol(show_qgis_areas.geometryType(), result['operation_config']['pg'][index_db]['estiloTabelasCamadas'][index_layer])
                show_qgis_areas.renderer().setSymbol(symbol)
                QgsProject.instance().addMapLayer(show_qgis_areas)
                index_layer += 1
            index_db += 1

        show_qgis_input = QgsVectorLayer(input.to_json(), "Lote")

        symbol = self.get_input_symbol(show_qgis_input.geometryType())
        show_qgis_input.renderer().setSymbol(symbol)

        QgsProject.instance().addMapLayer(show_qgis_input)

        if len(input_standard) > 0:
            show_qgis_input_standard = QgsVectorLayer(input_standard.to_json(), "Lote (padrão)")

            symbol = self.get_input_standard_symbol(show_qgis_input_standard.geometryType())
            show_qgis_input_standard.renderer().setSymbol(symbol)

            QgsProject.instance().addMapLayer(show_qgis_input_standard)

        # Repaint the canvas map
        iface.mapCanvas().refresh()
        # Da zoom na camada de input
        iface.zoomToActiveLayer()

    def print_overlay_qgis(self, result):
        input = result['input']
        input_standard = result['input_standard']

        gdf_selected_shp = result['gdf_selected_shp']
        gdf_selected_db = result['gdf_selected_db']

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
                show_qgis_areas = QgsVectorLayer(gdf_area.to_json(), result['operation_config']['shp'][index]['nomeFantasiaCamada'])

                symbol = self.get_feature_symbol(show_qgis_areas.geometryType(), result['operation_config']['shp'][index]['estiloCamadas'][0])
                print("Geometria: ", show_qgis_areas.geometryType())
                show_qgis_areas.renderer().setSymbol(symbol)
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
                                                     result['operation_config']['pg'][index_db][
                                                         'nomeFantasiaTabelasCamadas'][index_layer])
                    symbol = self.get_feature_symbol(show_qgis_areas.geometryType(), result['operation_config']['pg'][index_db]['estiloTabelasCamadas'][index_layer])
                    print("Geometria: ", show_qgis_areas.geometryType())
                    show_qgis_areas.renderer().setSymbol(symbol)
                    QgsProject.instance().addMapLayer(show_qgis_areas)

                index_layer += 1
            index_db += 1

        if print_input:
            gdf_input = gdf_input.drop_duplicates()

            show_qgis_input = QgsVectorLayer(gdf_input.to_json(), "Lote")

            symbol = self.get_input_symbol(show_qgis_input.geometryType())
            show_qgis_input.renderer().setSymbol(symbol)

            QgsProject.instance().addMapLayer(show_qgis_input)

            if len(input_standard) > 0:
                input_standard = input_standard.to_crs(4326)
                # gdf_input = gdf_input.to_crs(4326)
                get_overlay_standard = gpd.GeoDataFrame(columns=input_standard.columns)
                # Teste com shapefile
                for area in gdf_selected_shp:
                    for indexArea, rowArea in area.iterrows():
                        for indexInput, rowInput in input.iterrows():
                            if rowInput['geometry'].intersection(rowArea['geometry']):
                                get_overlay_standard = gpd.GeoDataFrame(pd.concat([get_overlay_standard, input_standard.iloc[[indexInput]]]))

                # Teste com banco de dados
                index_db = 0
                for db in gdf_selected_db:
                    index_layer = 0
                    for area in db:
                        if 'geom' in area:
                            area = area.drop(columns=['geom'])

                        for indexInput, rowInput in input.iterrows():
                            if rowInput['geometry'].intersection(rowArea['geometry']):
                                get_overlay_standard = gpd.GeoDataFrame(
                                    pd.concat([get_overlay_standard, input_standard.iloc[[indexInput]]]))
                        index_layer += 1
                    index_db += 1

                get_overlay_standard = get_overlay_standard.drop_duplicates()
                get_overlay_standard = get_overlay_standard.reset_index()

                show_qgis_input_standard = QgsVectorLayer(get_overlay_standard.to_json(), "Lote (padrão)")

                symbol = self.get_input_standard_symbol(show_qgis_input_standard.geometryType())
                show_qgis_input_standard.renderer().setSymbol(symbol)

                QgsProject.instance().addMapLayer(show_qgis_input_standard)

            # Repaint the canvas map
            iface.mapCanvas().refresh()
            # Da zoom na camada de input
            iface.zoomToActiveLayer()

    # Estilização dinâmica para diferentes tipos de geometrias (Área de input)
    def get_input_symbol(self, geometry_type):
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

    # Estilização dinâmica para diferentes tipos de geometrias (Área de input sem o buffer de aproximação)
    def get_input_standard_symbol(self, geometry_type):
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

    # Estilização dinâmica para diferentes tipos de geometrias (Áreas de comparação)
    def get_feature_symbol(self, geometry_type, style):
        symbol = None

        # Point
        if geometry_type == 0:
            symbol = QgsMarkerSymbol.createSimple(style)
        # Line String
        if geometry_type == 1:
            symbol = QgsLineSymbol.createSimple(style)
        # Polígono
        elif geometry_type == 2:
            symbol = QgsFillSymbol.createSimple(style)

        return symbol