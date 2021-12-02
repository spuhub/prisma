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
        epsg_shp = gpd.read_file(self.epsg_shp_dir)
        epsg_shp = epsg_shp.to_crs(epsg='4674')
        input = input.to_crs(epsg='4674')

        index = 0
        input['crs_feature'] = None
        for area in gdf_selected_shp:
            area = area.to_crs(epsg='4674')
            for indexInput, rowInput in input.iterrows():
                # Cálculos de área de input, centroid, etc
                input.loc[indexInput, 'areaLote'] = rowInput['geometry'].area
                input.loc[indexInput, 'ctr_lat'] = rowInput['geometry'].centroid.y
                input.loc[indexInput, 'ctr_long'] = rowInput['geometry'].centroid.x

                # Verifica fuso das features do input
                for indexEpsg, rowEpsg in epsg_shp.iterrows():
                    if (rowInput['geometry'].intersection(rowEpsg['geometry'])):
                        if input.iloc[indexInput]['crs_feature'] == None:
                            input.loc[indexInput, 'crs_feature'] = rowEpsg['EPSG_S2000']
                        else:
                            # Faz parte de dois ou mais fusos horário
                            input.loc[indexInput, 'crs_feature'] = False

                for indexArea, rowArea in area.iterrows():
                    input.loc[indexInput, self.result['operation_config']['shp'][index]['nome']] = rowArea['geometry'].intersection(rowInput['geometry']).area

                if input.iloc[indexInput]['crs_feature'] != False:
                    self.load_layer(input.loc[[indexInput]], area, index)

            index += 1

    def load_layer(self, feature_input_gdp, feature_area, index):
        crs = (feature_input_gdp.iloc[0]['crs_feature'])
        get_extent = feature_input_gdp.to_crs(crs)
        extent = get_extent.bounds
        print(extent)

        QgsProject.instance().setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))
        QApplication.instance().processEvents()
        # # Carrega camada mundial do OpenStreetMap
        tms = 'type=xyz&url=http://a.tile.openstreetmap.org/{z}/{x}/{y}.png'
        layer = QgsRasterLayer(tms, 'OpenStreetMap', 'wms')
        QgsProject.instance().addMapLayer(layer)
        QApplication.instance().processEvents()

        show_qgis_areas = QgsVectorLayer(feature_area.to_json(),
                                         self.result['operation_config']['shp'][index]['nomeFantasiaCamada'])
        symbol = QgsFillSymbol.createSimple(self.result['operation_config']['shp'][index]['estiloCamadas'][0])
        show_qgis_areas.renderer().setSymbol(symbol)
        QgsProject.instance().addMapLayer(show_qgis_areas)
        QApplication.instance().processEvents()

        # Carrega camada de input
        show_qgis_input = QgsVectorLayer(feature_input_gdp.to_json(), "Lote")

        symbol = QgsFillSymbol.createSimple(
            {'line_style': 'solid', 'line_color': 'black', 'color': 'gray', 'width_border': '0,35',
             'style': 'solid'})
        show_qgis_input.renderer().setSymbol(symbol)
        QgsProject.instance().addMapLayer(show_qgis_input)
        QApplication.instance().processEvents()

        print("CRS da feature: ", crs)
        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() == 'Lote':
                rect = QgsRectangle(extent['minx'], extent['miny'], extent['maxx'], extent['maxy'])
                layer.setExtent(rect)
                self.layers = layer

        ms = QgsMapSettings()
        ms.setLayers([self.layers])
        rect = QgsRectangle(ms.fullExtent())
        rect.scale(1.2)

        main_map = self.layout.itemById('Planta_Principal')
        localization_map = self.layout.itemById('Planta_Localizacao')
        situation_map = self.layout.itemById('Planta_Situacao')

        ms.setExtent(rect)
        # map.setExtent(rect)
        main_map.zoomToExtent(rect)

        rect.scale(1.5)
        localization_map.setExtent(rect)
        localization_map.zoomToExtent(rect)

        rect.scale(2.0)
        situation_map.zoomToExtent(rect)

        # Tamanho do mapa no layout
        main_map.attemptResize(QgsLayoutSize(390, 277, QgsUnitTypes.LayoutMillimeters))
        localization_map.attemptResize(QgsLayoutSize(65, 65, QgsUnitTypes.LayoutMillimeters))
        situation_map.attemptResize(QgsLayoutSize(65, 65, QgsUnitTypes.LayoutMillimeters))

        self.pdf_generator(feature_input_gdp, feature_area, index)

        # Remove camadas já impressas
        QgsProject.instance().removeAllMapLayers()


    def pdf_generator(self, feature_input_gdp, feature_area, index):
        # Manipulação dos textos do layout
        # self.handle_text()

        pdf_name = str(feature_input_gdp.iloc[0]['logradouro']) + '_' + str(self.result['operation_config']['shp'][index]['nomeFantasiaCamada']) + '.pdf'

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
