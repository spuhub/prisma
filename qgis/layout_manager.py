import os

from qgis import processing

from qgis.PyQt.QtWidgets import QApplication
from qgis.core import *
from qgis.PyQt.QtXml import QDomDocument
from qgis.utils import iface
from PyQt5.QtCore import QTimer
from .map_canvas import MapCanvas

import geopandas as gpd

class LayoutManager():
    def __init__(self, result):
        super().__init__()
        self.result = result
        # Adiciona o layout ao projeto atual
        template_dir = os.path.join(os.path.dirname(__file__), 'layouts\Modelo_Layout_A3.qpt')
        self.add_template_to_project(template_dir)

        # Armazena na variável o layout que acabou de ser adicionado
        # ao projeto, permitindo a manipulação do mesmo
        self.layout = None
        self.layers = []

        # Diretório do shapefile para gerar dinamicamente os EPSG's
        self.epsg_shp_dir = os.path.join(os.path.dirname(__file__), '..\shapefiles\Zonas_UTM_BR-EPSG4326.shp')

    def export_pdf(self):
        self.layout = QgsProject.instance().layoutManager().layoutByName("FolhaA3_Planta_Retrato")
        # Armazena as camadas em self.layers e adiciona as camadas no QGis
        self.process_layer()
        # Manipulação dos textos do layout
        # self.handle_text()

    def process_layer(self):
        input = self.result['input']
        gdf_selected_shp = self.result['gdf_selected_shp']
        gdf_selected_db = self.result['gdf_selected_db']
        # Verifica fuso das features do input
        input = self.get_utm_crs(input)

        for indexInput, rowInput in input.iterrows():
            if rowInput['crs_feature'] != False:
                self.calculation_shp(input.loc[[indexInput]], gdf_selected_shp)
                self.calculation_db(input.loc[[indexInput]], gdf_selected_db)

    def calculation_shp(self, input, gdf_selected_shp):
        input = input.reset_index()
        intersection = []

        crs = 'EPSG:' + str(input.loc[0]['crs_feature'])
        input = input.to_crs(crs)

        index = 0
        for area in gdf_selected_shp:
            area = area.to_crs(crs)
            # Cálculos de área de input, centroid, etc
            input.loc[0, 'areaLote'] = input.loc[0]['geometry'].area
            input.loc[0, 'ctr_lat'] = input.loc[0]['geometry'].centroid.y
            input.loc[0, 'ctr_long'] = input.loc[0]['geometry'].centroid.x

            for indexArea, rowArea in area.iterrows():
                input.loc[0, self.result['operation_config']['shp'][index]['nome']] = rowArea[
                    'geometry'].intersection(input.loc[0]['geometry']).area
                if (input.loc[0]['geometry'].intersection(rowArea['geometry'])):
                    data = {
                        'areaLote': input.loc[0]['geometry'].intersection(rowArea['geometry']).area,
                        'ctr_lat': input.loc[0]['geometry'].intersection(rowArea['geometry']).centroid.y,
                        'ctr_long': input.loc[0]['geometry'].intersection(rowArea['geometry']).centroid.x,
                        'geometry': [input.loc[0]['geometry'].intersection(rowArea['geometry'])]
                    }

                    intersection = gpd.GeoDataFrame(data, crs=input.crs)
                self.load_layer(input.loc[[0]], area, intersection, index, None)
            index += 1

    def calculation_db(self, input, gdf_selected_db):
        input = input.reset_index()
        intersection = []

        crs = 'EPSG:' + str(input.loc[0]['crs_feature'])
        input = input.to_crs(crs)

        index_db = 0
        for db in gdf_selected_db:
            index_layer = 0
            for area in db:
                area.crs = 'EPSG:4674'
                area = area.to_crs(crs)
                # Cálculos de área de input, centroid, etc
                input.loc[0, 'areaLote'] = input.loc[0]['geometry'].area
                input.loc[0, 'ctr_lat'] = input.loc[0]['geometry'].centroid.y
                input.loc[0, 'ctr_long'] = input.loc[0]['geometry'].centroid.x

                for indexArea, rowArea in area.iterrows():
                    input.loc[0, self.result['operation_config']['pg'][index_db]['nomeFantasiaTabelasCamadas'][
                        index_layer]] = rowArea['geometry'].intersection(input.loc[0]['geometry']).area

                    if (input.loc[0]['geometry'].intersection(rowArea['geometry'])):
                        data = {
                            'areaLote': input.loc[0]['geometry'].intersection(rowArea['geometry']).area,
                            'ctr_lat': input.loc[0]['geometry'].intersection(rowArea['geometry']).centroid.y,
                            'ctr_long': input.loc[0]['geometry'].intersection(rowArea['geometry']).centroid.x,
                            'geometry': [input.loc[0]['geometry'].intersection(rowArea['geometry'])]
                        }

                        intersection = gpd.GeoDataFrame(data, crs=input.crs)

                    self.load_layer(input.loc[[0]], area, intersection, index_db, index_layer)
                index_layer += 1
            index_db += 1
    def get_utm_crs(self, input):
        input['crs_feature'] = None
        epsg_shp = gpd.read_file(self.epsg_shp_dir)
        epsg_shp = epsg_shp.to_crs(epsg='4674')

        for indexInput, rowInput in input.iterrows():
            for indexEpsg, rowEpsg in epsg_shp.iterrows():
                if (rowInput['geometry'].intersection(rowEpsg['geometry'])):
                    if input.iloc[indexInput]['crs_feature'] == None:
                        input.loc[indexInput, 'crs_feature'] = rowEpsg['EPSG_S2000']
                    else:
                        # Faz parte de dois ou mais fusos horário
                        input.loc[indexInput, 'crs_feature'] = False

        return input

    def load_layer(self, feature_input_gdp, feature_area, feature_intersection, index_1, index_2):
        crs = (feature_input_gdp.iloc[0]['crs_feature'])
        get_extent = feature_input_gdp.to_crs(crs)
        extent = feature_input_gdp.bounds

        feature_input_gdp = feature_input_gdp.to_crs(4674)
        feature_area = feature_area.to_crs(4674)

        QgsProject.instance().setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))
        QApplication.instance().processEvents()
        # Carrega camada mundial do OpenStreetMap
        tms = 'type=xyz&url=http://a.tile.openstreetmap.org/{z}/{x}/{y}.png'
        layer = QgsRasterLayer(tms, 'OpenStreetMap', 'wms')
        QgsProject.instance().addMapLayer(layer)

        if index_2 == None:
            print(self.result['operation_config']['shp'][index_1]['nomeFantasiaCamada'])
            show_qgis_areas = QgsVectorLayer(feature_area.to_json(),
                                             self.result['operation_config']['shp'][index_1]['nomeFantasiaCamada'])
            symbol = QgsFillSymbol.createSimple(self.result['operation_config']['shp'][index_1]['estiloCamadas'][0])
            show_qgis_areas.renderer().setSymbol(symbol)
            QgsProject.instance().addMapLayer(show_qgis_areas)
        else:
            if 'geom' in feature_area:
                feature_area = feature_area.drop(columns=['geom'])

            feature_area = feature_area.drop_duplicates()

            show_qgis_areas = QgsVectorLayer(feature_area.to_json(),
                                             self.result['operation_config']['pg'][index_1]['nomeFantasiaTabelasCamadas'][index_2])
            symbol = QgsFillSymbol.createSimple(self.result['operation_config']['pg'][index_1]['estiloTabelasCamadas'][index_2])
            show_qgis_areas.renderer().setSymbol(symbol)
            QgsProject.instance().addMapLayer(show_qgis_areas)

        # Carrega camada de input
        show_qgis_input = QgsVectorLayer(feature_input_gdp.to_json(), "Lote")

        symbol = QgsFillSymbol.createSimple(
            {'line_style': 'solid', 'line_color': 'black', 'color': 'gray', 'width_border': '0,35',
             'style': 'solid'})
        show_qgis_input.renderer().setSymbol(symbol)
        QgsProject.instance().addMapLayer(show_qgis_input)

        if len(feature_intersection) > 0:
            feature_intersection = feature_intersection.to_crs(4674)
            show_qgis_intersection = QgsVectorLayer(feature_intersection.to_json(), "Sobreposição")

            symbol = QgsFillSymbol.createSimple(
                {'line_style': 'solid', 'line_color': 'black', 'color': 'yellow', 'width_border': '0,35',
                 'style': 'solid'})
            show_qgis_intersection.renderer().setSymbol(symbol)
            QgsProject.instance().addMapLayer(show_qgis_intersection)

        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() == 'Lote':
                rect = QgsRectangle(extent['minx'], extent['miny'], extent['maxx'], extent['maxy'])
                layer.setExtent(rect)
                self.layers = layer

        ms = QgsMapSettings()
        ms.setLayers([self.layers])
        rect = QgsRectangle(ms.fullExtent())

        rect.scale(1.3)

        main_map = self.layout.itemById('Planta_Principal')
        localization_map = self.layout.itemById('Planta_Localizacao')
        situation_map = self.layout.itemById('Planta_Situacao')

        ms.setExtent(rect)
        main_map.zoomToExtent(rect)
        localization_map.setScale(main_map.scale() * 1250)
        # situation_map.zoomToExtent(rect)
        situation_map.setScale(main_map.scale() * 25)

        # Tamanho do mapa no layout
        main_map.attemptResize(QgsLayoutSize(390, 277, QgsUnitTypes.LayoutMillimeters))

        self.pdf_generator(feature_input_gdp, feature_area, index_1, index_2)

        # Remove camadas já impressas
        QgsProject.instance().removeAllMapLayers()


    def pdf_generator(self, feature_input_gdp, feature_area, index_1, index_2):
        # Manipulação dos textos do layout
        # self.handle_text()

        if index_2 == None:
            pdf_name = str(feature_input_gdp.iloc[0]['logradouro']) + '_' + str(self.result['operation_config']['shp'][index_1]['nomeFantasiaCamada']) + '.pdf'
        else:
            pdf_name = str(feature_input_gdp.iloc[0]['logradouro']) + '_' + str(self.result['operation_config']['pg'][index_1]['nomeFantasiaTabelasCamadas'])[index_2] + '.pdf'

        pdf_path = os.path.join(r'C:\Users\vinir\Documents\saida', pdf_name)
        exporter = QgsLayoutExporter(self.layout)
        exporter.exportToPdf(pdf_path, QgsLayoutExporter.PdfExportSettings())

        QApplication.instance().processEvents()


    def handle_text(self):
        title = self.layout.itemById('CD_Titulo')
        title.setText('Teste 123')

        scale = self.layout.itemById('CD_Escala')
        scale.setText('1:' + str(round(iface.mapCanvas().scale())))

    # def load_layers(self):
    #     self.layers.append(QgsProject.instance().mapLayersByName('input')[0])
    #
    #     # Pega camadas através dos nomes
    #     if len(self.result['operation_config']['shp']) != 0:
    #         print(len(self.result['operation_config']['shp']))
    #         for i in range(len(self.result['operation_config']['shp'])):
    #             vlayer = QgsProject.instance().mapLayersByName(self.result['operation_config']['shp'][i]['nomeFantasiaCamada'])
    #             if len(vlayer) > 0:
    #                 self.layers.append(vlayer[0])
    #
    #     if len(self.result['operation_config']['pg']) != 0:
    #         print(len(self.result['operation_config']['pg']))
    #         for i in range(len(self.result['operation_config']['pg'])):
    #             for j in range(len(self.result['operation_config']['pg'][i]['nomeFantasiaTabelasCamadas'])):
    #                 vlayer = QgsProject.instance().mapLayersByName(self.result['operation_config']['pg'][i]['nomeFantasiaTabelasCamadas'][j])
    #                 if len(vlayer) > 0:
    #                     self.layers.append(vlayer[0])
    #
    #     ms = QgsMapSettings()
    #     ms.setLayers(self.layers)
    #     rect = QgsRectangle(ms.fullExtent())
    #     rect.scale(1.0)
    #
    #     map = self.layout.itemById('Planta_Principal')
    #
    #     ms.setExtent(rect)
    #     map.setExtent(rect)
    #
    #     # Tamanho do mapa no layout
    #     map.attemptResize(QgsLayoutSize(390, 277, QgsUnitTypes.LayoutMillimeters))

    def add_template_to_project(self, template_dir):
        project = QgsProject.instance()
        layout = QgsPrintLayout(project)
        document = QDomDocument()

        # Leitura do template
        template_file = open(template_dir)
        template_content = template_file.read()
        template_file.close()
        document.setContent(template_content)

        # Adição do template no projeto
        layout.loadFromTemplate(document, QgsReadWriteContext())
        project.layoutManager().addLayout(layout)
