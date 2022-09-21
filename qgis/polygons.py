# -*- coding: utf-8 -*-
import os

from qgis.PyQt.QtWidgets import QApplication
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsRasterLayer, QgsVectorLayer, QgsFillSymbol, \
    QgsLineSymbol, QgsMarkerSymbol, QgsRectangle, QgsMapSettings, QgsLayoutSize, QgsUnitTypes, QgsLayoutExporter, \
    QgsPrintLayout, QgsReadWriteContext, QgsPalLayerSettings, QgsTextFormat, QgsVectorLayerSimpleLabeling
from qgis.PyQt.QtXml import QDomDocument
from qgis.utils import iface
from PyQt5.QtCore import Qt

from ..utils.utils import Utils
from ..settings.env_tools import EnvTools
from ..analysis.overlay_analysis import OverlayAnalisys

import geopandas as gpd
from shapely.geometry import Polygon, Point, LineString
from PyPDF2 import PdfFileReader, PdfFileMerger
from datetime import datetime
from .polygon_required import PolygonRequired
from .overlay_report_polygons import OverlayReportPolygons

from urllib.parse import quote

class Polygons():
    def __init__(self, operation_config):
        self.operation_config = operation_config

        self.layout = None
        self.atlas = None
        self.index_input = None
        self.overlay_report = OverlayReportPolygons()

        self.utils = Utils()
        self.time = None
        self.pd = PolygonRequired(self.operation_config)

        self.layers = []
        self.rect_main_map = None
        self.root = QgsProject.instance().layerTreeRoot()

        self.basemap = self.operation_config['operation_config']['basemap']['nome'] if 'basemap' in self.operation_config['operation_config'] else 'OpenStreetMap'

    def comparasion_between_polygons(self, input, input_standard, area, gdf_required, index_1, index_2, atlas, layout, index_input, last_area):
        self.atlas = atlas
        self.layout = layout

        input, intersection_required = self.calculation_required(input, gdf_required)
        # Extrai vértices e linhas do polígono que está sendo comparado
        gdf_point_input, gdf_line_input = self.explode_input(input)

        # Cálculos de área e centroid da feição de input
        input.loc[0, 'areaLote'] = input.iloc[0]['geometry'].area
        input.loc[0, 'ctr_lat'] = input.iloc[0]['geometry'].centroid.y
        input.loc[0, 'ctr_long'] = input.iloc[0]['geometry'].centroid.x

        # Soma da área de interseção feita com feição de input e atual área comparada
        # Essa soma é atribuida a uma nova coluna, identificada pelo nome da área comparada. Ex área quilombola: 108.4
        if index_2 == None:
            input.loc[0, self.operation_config['operation_config']['shp'][index_1]['nomeFantasiaCamada']] = gpd.overlay(
                input, area).area.sum()
        else:
            input.loc[0, self.operation_config['operation_config']['pg'][index_1]['nomeFantasiaTabelasCamadas'][
                index_2]] = gpd.overlay(input, area).area.sum()

        # Pega o tempo em que o processamento da feição atual se inicia
        # Utilizado para gerar os nomes únicos na hora de exportar o PDF
        if index_input != self.index_input:
            self.index_input = index_input
            date_and_time = datetime.now()
            self.time = date_and_time.strftime('%Y-%m-%d_%H-%M-%S')
            # Gera o layout PDF com a área de entrada e áreas da união
            self.pd.polygon_required_layers(input, input_standard, intersection_required, gdf_line_input, gdf_point_input, self.index_input,
                                            self.time, self.atlas, self.layout)

        data = []
        # Armazena em um novo GeoDataFrame (intersection) as áreas de interseção entre feição de entrada e feição
        # da atual área que está sendo comparada. Realiza ainda cálculo de área e centroid para a nova geomatria de interseção
        for indexArea, rowArea in area.iterrows():
            if (input.iloc[0]['geometry'].intersection(rowArea['geometry'])):
                data.append({
                    'areaLote': input.iloc[0]['geometry'].intersection(rowArea['geometry']).area,
                    'ctr_lat': input.iloc[0]['geometry'].intersection(rowArea['geometry']).centroid.y,
                    'ctr_long': input.iloc[0]['geometry'].intersection(rowArea['geometry']).centroid.x,
                    'geometry': input.iloc[0]['geometry'].intersection(rowArea['geometry'])
                })

        # Corrigido problema onde lista 'data' chegava ao dataframe vazia.
        intersection = gpd.GeoDataFrame(data, crs=input.crs) if len(data) > 0 else None

        # Gera planta pdf somente quando acontece sobreposição
        # Corrigido problema onde pode não haver dataframe, pois a lista 'data' estava vazia
        if intersection is not None:
            if len(intersection) > 0:
                intersection.set_crs(allow_override=True, crs=input.crs)

                if len(input_standard) > 0:
                    self.handle_comparasion_layers(input.iloc[[0]], gdf_line_input, gdf_point_input, input_standard.iloc[[0]], area,
                                    intersection, gdf_required, index_1, index_2)
                else:
                    self.handle_comparasion_layers(input.iloc[[0]], gdf_line_input, gdf_point_input, input_standard, area, intersection,
                                    gdf_required, index_1, index_2)

        if last_area:
            self.overlay_report.handle_overlay_report(input, self.operation_config, self.time, index_1, index_2)

        input = input.reset_index(drop=True)
        return input

    def calculation_required(self, input, gdf_required):
        input = input.reset_index(drop=True)
        intersection = None

        crs = 'EPSG:' + str(input.iloc[0]['crs_feature'])

        input = input.to_crs(crs)
        input.set_crs(crs, allow_override=True)

        if 'aproximacao' in self.operation_config['operation_config']:
            input = self.utils.add_input_approximation_projected(input, self.operation_config['operation_config'][
                'aproximacao'])

        index = 0
        # Compara a feição de entrada com todas as áreas de comparação obrigatórias selecionadas pelo usuário
        for area in gdf_required:
            if len(area) > 0:
                if isinstance(area, list):
                    area = area[0].to_crs(crs)
                else:
                    area = area.to_crs(crs)
                area = area.to_crs(crs)
                area.set_crs(allow_override=True, crs=crs)

                if 'nomeFantasiaCamada' in self.operation_config['operation_config']['required'][index]:
                    if self.operation_config['operation_config']['required'][index][
                        "nomeFantasiaCamada"] == "Área Homologada" or \
                            self.operation_config['operation_config']['required'][index][
                                "nomeFantasiaCamada"] == "Área Não Homologada":
                        input.loc[0, self.operation_config['operation_config']['required'][index]['nomeFantasiaCamada']] = gpd.overlay(
                            input, area).area.sum()

                        if self.operation_config['operation_config']['required'][index][
                            "nomeFantasiaCamada"] == "Área Homologada":
                            data = []
                            # Armazena em um novo GeoDataFrame (intersection) as áreas de interseção entre feição de entrada e área homologada.
                            # Realiza ainda cálculo de área e centroid para a nova geomatria de interseção
                            for indexArea, rowArea in area.iterrows():
                                if (input.iloc[0]['geometry'].intersection(rowArea['geometry'])):
                                    data.append({
                                        'geometry': input.iloc[0]['geometry'].intersection(rowArea['geometry'])
                                    })

                            # Corrigido problema onde lista 'data' chegava ao dataframe vazia.
                            intersection = gpd.GeoDataFrame(data, crs=input.crs) if len(data) > 0 else None

                    else:
                        has_overlay = len(gpd.overlay(area, input))
                        if has_overlay > 0:
                            input.loc[0, self.operation_config['operation_config']['required'][index][
                                'nomeFantasiaCamada']] = True
                        else:
                            input.loc[0, self.operation_config['operation_config']['required'][index][
                                'nomeFantasiaCamada']] = False
                else:
                    if self.operation_config['operation_config']['required'][index][
                        "nomeFantasiaTabelasCamadas"][0] == "Área Homologada" or \
                            self.operation_config['operation_config']['required'][index][
                                "nomeFantasiaTabelasCamadas"][0] == "Área Não Homologada":
                        input.loc[0, self.operation_config['operation_config']['required'][index][
                            'nomeFantasiaTabelasCamadas']] = gpd.overlay(
                            input, area).area.sum()

                        if self.operation_config['operation_config']['required'][index][
                            "nomeFantasiaTabelasCamadas"][0] == "Área Homologada":
                            data = []
                            # Armazena em um novo GeoDataFrame (intersection) as áreas de interseção entre feição de entrada e área homologada.
                            # Realiza ainda cálculo de área e centroid para a nova geomatria de interseção
                            for indexArea, rowArea in area.iterrows():
                                if (input.iloc[0]['geometry'].intersection(rowArea['geometry'])):
                                    data.append({
                                        'geometry': input.iloc[0]['geometry'].intersection(rowArea['geometry'])
                                    })

                            # Corrigido problema onde lista 'data' chegava ao dataframe vazia.
                            intersection = gpd.GeoDataFrame(data, crs=input.crs) if len(data) > 0 else None
                    else:
                        has_overlay = len(gpd.overlay(area, input))
                        if has_overlay > 0:
                            input.loc[0, self.operation_config['operation_config']['required'][index][
                                'nomeFantasiaTabelasCamadas']] = True
                        else:
                            input.loc[0, self.operation_config['operation_config']['required'][index][
                                'nomeFantasiaTabelasCamadas']] = False
            index += 1
        input = input.reset_index(drop=True)
        return input, intersection

    def explode_input(self, gdf_input):
        geometry = gdf_input.iloc[0]['geometry']

        geometry_points = []
        coord_x = []
        coord_y = []
        geometry_lines = []

        if geometry.type == 'Polygon':
            all_coords = geometry.exterior.coords

            for coord in all_coords:
                geometry_points.append(Point(coord))
                coord_x.append(list(coord)[0])
                coord_y.append(list(coord)[1])

            for i in range(1, len(all_coords)):
                geometry_lines.append(LineString([all_coords[i - 1], all_coords[i]]))

        if geometry.type == 'MultiPolygon':
            all_coords = []
            for ea in geometry:
                all_coords.append(list(ea.exterior.coords))

            for polygon in all_coords:
                for coord in polygon:
                    geometry_points.append(Point(coord))
                    coord_x.append(list(coord)[0])
                    coord_y.append(list(coord)[1])

            for polygon in all_coords:
                for i in range(1, len(polygon)):
                    geometry_lines.append(LineString([polygon[i - 1], polygon[i]]))

        data = list(zip(coord_x, coord_y, geometry_points))

        gdf_geometry_points = gpd.GeoDataFrame(columns=['coord_x', 'coord_y', 'geometry'], data=data, crs=gdf_input.crs)
        gdf_geometry_lines = gpd.GeoDataFrame(geometry=geometry_lines, crs=gdf_input.crs)

        return gdf_geometry_points, gdf_geometry_lines

    def handle_comparasion_layers(self, feature_input_gdp, gdf_line_input, gdf_point_input, input_standard, feature_area, feature_intersection, gdf_required, index_1, index_2):
        """
        Carrega camadas já processadas no QGis para que posteriormente possam ser gerados os relatórios no formato PDF. Após gerar todas camadas necessárias,
        está função aciona outra função (export_pdf), que é responsável por gerar o layout PDF a partir das feições carregadas nesta função.

        @keyword feature_input_gdp: Feição que está sendo processada e será carregada para o QGis.
        @keyword input_standard: Feição padrão isto é, sem zona de proximidade (caso necessário), que está sendo processada e será carregada para o QGis.
        @keyword feature_area: Camada de comparação que está sendo processada.
        @keyword feature_intersection: Camada de interseção (caso exista) e será carregada para o QGis.
        @keyword index_1: Variável utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar informções como estilização ou nome da camada.
        @keyword index_2: Variável utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar informções como estilização ou nome da camada.
        """
        crs = (feature_input_gdp.iloc[0]['crs_feature'])
        # Forma de contornar problema do QGis, que alterava o extent da camada de forma incorreta
        extent = feature_input_gdp.bounds

        # Altera o EPSG do projeto QGis
        QgsProject.instance().setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))
        QApplication.instance().processEvents()

        self.remove_layers()

        # len(QgsProject.instance().layerTreeRoot().children()) # usar depois
        # self.root.insertLayer(0, self.root.layerOrder()[3]) # usar depois

        # self.root.insertLayer(len(QgsProject.instance().layerTreeRoot().children()) - 2, )

        # Carrega as áreas de intersecção no Qgis
        if len(feature_intersection) > 0:
            show_qgis_intersection = QgsVectorLayer(feature_intersection.to_json(), "Sobreposição")
            show_qgis_intersection.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

            show_qgis_intersection.loadSldStyle(self.operation_config['operation_config']['sld_default_layers']['overlay_input_polygon'])
            QgsProject.instance().addMapLayer(show_qgis_intersection, False)
            self.root.insertLayer(len(QgsProject.instance().layerTreeRoot().children()) - 1, show_qgis_intersection)

        # Carrega a área padrão no QGis, sem área de aproximação (caso necessário)
        if 'aproximacao' in self.operation_config['operation_config']:
            # Carrega camada de input no QGis (Caso usuário tenha inserido como entrada, a área de aproximação está nesta camada)
            show_qgis_input = QgsVectorLayer(feature_input_gdp.to_json(), "Feição de Estudo/Sobreposição")
            show_qgis_input.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

            symbol = self.get_input_symbol(show_qgis_input.geometryType())
            show_qgis_input.renderer().setSymbol(symbol)
            QgsProject.instance().addMapLayer(show_qgis_input, False)
            self.root.insertLayer(len(QgsProject.instance().layerTreeRoot().children()) - 1, show_qgis_input)

            if index_2 != None:
                input_standard = input_standard.to_crs(crs)
            show_qgis_input_standard = QgsVectorLayer(input_standard.to_json(),
                                                      "Feição de Estudo/Sobreposição (padrão)")
            show_qgis_input_standard.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

            symbol = self.get_input_standard_symbol(show_qgis_input_standard.geometryType())
            show_qgis_input_standard.renderer().setSymbol(symbol)
            QgsProject.instance().addMapLayer(show_qgis_input_standard, False)
            self.root.insertLayer(len(QgsProject.instance().layerTreeRoot().children()) - 2, show_qgis_input_standard)
        else:
            # Carrega camada de input no QGis (Caso usuário tenha inserido como entrada, a área de aproximação está nesta camada)
            show_qgis_input = QgsVectorLayer(feature_input_gdp.to_json(), "Feição de Estudo/Sobreposição")
            show_qgis_input.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

            symbol = self.get_input_standard_symbol(show_qgis_input.geometryType())
            show_qgis_input.renderer().setSymbol(symbol)
            QgsProject.instance().addMapLayer(show_qgis_input, False)
            self.root.insertLayer(len(QgsProject.instance().layerTreeRoot().children()) - 1, show_qgis_input)

        # Carrega camada de comparação no QGis
        # Se index 2 é diferente de None, significa que a comparação está vinda de banco de dados
        if index_2 == None:
            show_qgis_areas = QgsVectorLayer(feature_area.to_json(),
                                             self.operation_config['operation_config']['shp'][index_1][
                                                 'nomeFantasiaCamada'])
            show_qgis_areas.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

            show_qgis_areas.loadSldStyle(self.operation_config['operation_config']['shp'][index_1]['estiloCamadas'][0]['stylePath'])
            QgsProject.instance().addMapLayer(show_qgis_areas, False)
            self.root.insertLayer(len(QgsProject.instance().layerTreeRoot().children()) - 1, show_qgis_areas)
        else:
            if 'geom' in feature_area:
                feature_area = feature_area.drop(columns=['geom'])

            feature_area = feature_area.drop_duplicates()

            show_qgis_areas = QgsVectorLayer(feature_area.to_json(),
                                             self.operation_config['operation_config']['pg'][index_1][
                                                 'nomeFantasiaTabelasCamadas'][index_2])
            show_qgis_areas.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

            show_qgis_areas.loadSldStyle(
                self.operation_config['operation_config']['pg'][index_1]['estiloTabelasCamadas'][index_2]['stylePath'])
            QgsProject.instance().addMapLayer(show_qgis_areas, False)
            self.root.insertLayer(len(QgsProject.instance().layerTreeRoot().children()) - 1, show_qgis_areas)

        # Camada de cotas
        show_qgis_quota = QgsVectorLayer(gdf_line_input.to_json(), "Linhas")
        show_qgis_quota.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

        QgsProject.instance().addMapLayer(show_qgis_quota, False)
        self.root.insertLayer(0, show_qgis_quota)

        # Camada de vértices
        # Remover o último vértice, para não ficar dois pontos no mesmo lugar
        show_gdf_point_input = gdf_point_input[:-1]
        show_qgis_vertices = QgsVectorLayer(show_gdf_point_input.to_json(), "Vértices")
        show_qgis_vertices.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

        QgsProject.instance().addMapLayer(show_qgis_vertices, False)
        self.root.insertLayer(0, show_qgis_vertices)

        layers_localization_map = []
        layers_situation_map = []
        # Posiciona a tela do QGis no extent da área de entrada
        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() == 'Feição de Estudo/Sobreposição':
                rect = QgsRectangle(extent['minx'], extent['miny'], extent['maxx'], extent['maxy'])
                # Aqui está sendo contornado o erro de transformação, comentado no comeco desta função
                layer.setExtent(rect)
                self.atlas.setEnabled(True)
                self.atlas.setCoverageLayer(layer)
                self.atlas.changed
                self.layers = layer

                layers_localization_map.append(layer)
                layers_situation_map.append(layer)

            elif layer.name() == self.basemap:
                layers_localization_map.append(layer)
                layers_situation_map.append(layer)

            elif layer.name() == 'Linhas':
                qml_style_dir = os.path.join(os.path.dirname(__file__), 'static\Estilo_Linhas_de_Cota_L.qml')
                layer.loadNamedStyle(qml_style_dir)
                layer.triggerRepaint()

            elif layer.name() == 'Vértices':
                qml_style_dir = os.path.join(os.path.dirname(__file__), 'static\Estilo_Vertice_P.qml')
                layer.loadNamedStyle(qml_style_dir)
                layer.triggerRepaint()

            if index_2 == None:
                if layer.name() == self.operation_config['operation_config']['shp'][index_1][
                                                     'nomeFantasiaCamada']:
                    layers_situation_map.insert(len(layers_situation_map) - 1, layer)
            else:
                if layer.name() == self.operation_config['operation_config']['pg'][index_1][
                                                 'nomeFantasiaTabelasCamadas'][index_2]:
                    layers_situation_map.insert(len(layers_situation_map) - 1, layer)

        # Configurações no QGis para gerar os relatórios PDF
        ms = QgsMapSettings()
        ms.setLayers([self.layers])
        rect = QgsRectangle(ms.fullExtent())

        main_map = self.layout.itemById('Planta_Principal')
        situation_map = self.layout.itemById('Planta_Situacao')
        localization_map = self.layout.itemById('Planta_Localizacao')

        situation_map.setLayers(layers_situation_map)
        localization_map.setLayers(layers_localization_map)
        situation_map.refresh()
        localization_map.refresh()

        ms.setExtent(rect)
        main_map.zoomToExtent(rect)
        iface.mapCanvas().refresh()
        main_map.refresh()
        QApplication.instance().processEvents()
        self.rect_main_map = main_map.extent()

        # Tamanho do mapa no layout
        main_map.attemptResize(QgsLayoutSize(390, 277, QgsUnitTypes.LayoutMillimeters))

        self.export_pdf(feature_input_gdp, gdf_point_input, index_1, index_2)

    def export_pdf(self, feature_input_gdp, gdf_point_input, index_1, index_2):
        """
        Função responsável carregar o layout de impressão e por gerar os arquivos PDF.

        @keyword feature_input_gdp: Feição de input comparada
        @keyword index_1: Variável utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar informções como estilização ou nome da camada.
        @keyword index_2: Variável utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar informções como estilização ou nome da camada.
        """
        # Manipulação dos textos do layout
        self.handle_text(feature_input_gdp, index_1, index_2)

        if 'logradouro' not in feature_input_gdp:
            feature_input_gdp['logradouro'] = "Ponto por Endereço ou Coordenada"

        if index_1 == None and index_2 == None:
            pdf_name = str(feature_input_gdp.iloc[0]['logradouro']) + '_' + str(self.time) + '_AreasObrigatorias.pdf'
        elif index_2 == None:
            pdf_name = str(feature_input_gdp.iloc[0]['logradouro']) + '_' + str(self.time) + '_' + str(
                self.operation_config['operation_config']['shp'][index_1]['nomeFantasiaCamada']) + '.pdf'
        else:
            pdf_name = str(feature_input_gdp.iloc[0]['logradouro']) + '_' + str(self.time) + '_' + str(
                self.operation_config['operation_config']['pg'][index_1]['nomeFantasiaTabelasCamadas'][
                    index_2]) + '.pdf'

        pdf_path = os.path.join(self.operation_config['path_output'], pdf_name)

        atlas = self.layout.atlas()
        """Armazena o atlas do layout de impressão carregado no projeto."""
        map_atlas = atlas.layout()
        pdf_settings = QgsLayoutExporter(map_atlas).PdfExportSettings()
        pdf_settings.dpi = 300

        if atlas.enabled():
            pdf_settings.rasterizeWholeImage = True
            QgsLayoutExporter.exportToPdf(atlas, pdf_path,
                                          settings=pdf_settings)

        self.merge_pdf(pdf_name)

    def merge_pdf(self, pdf_name):
        pdf_name = "_".join(pdf_name.split("_", 3)[:3])
        # files_dir = os.path.normpath(files_dir)
        # print(files_dir)
        pdf_files = [f for f in os.listdir(self.operation_config['path_output']) if f.startswith(pdf_name) and f.endswith(".pdf")]
        merger = PdfFileMerger()

        for filename in pdf_files:
            merger.append(PdfFileReader(os.path.join(self.operation_config['path_output'], filename), "rb"))

        merger.write(os.path.join(self.operation_config['path_output'], pdf_name + ".pdf"))

        for filename in os.listdir(self.operation_config['path_output']):
            if pdf_name in filename and filename.count("_") > 2:
                os.remove(self.operation_config['path_output'] + "/" + filename)

    def handle_text(self, feature_input_gdp, index_1, index_2):
        """
        Faz a manipulação de alguns dados textuais presentes no layout de impressão.

        @keyword index_1: Variável utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar informções como estilização ou nome da camada.
        @keyword index_2: Variável utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar informções como estilização ou nome da camada.
        """
        et = EnvTools()
        headers = et.get_report_hearder()

        spu = self.layout.itemById('CD_UnidadeSPU')
        spu.setText(headers['superintendencia'])

        sector = self.layout.itemById('CD_SubUnidadeSPU')
        sector.setText(headers['setor'])

        title = self.layout.itemById('CD_Titulo')
        if index_2 == None:
            layer_name = self.operation_config['operation_config']['shp'][index_1]['nomeFantasiaCamada']
            title.setText('Caracterização: ' + layer_name)
            self.fill_observation(feature_input_gdp, layer_name)
        else:
            layer_name = self.operation_config['operation_config']['pg'][index_1]['nomeFantasiaTabelasCamadas'][index_2]
            title.setText('Caracterização: ' + layer_name)
            self.fill_observation(feature_input_gdp, layer_name)

        self.fill_data_source()

    def fill_data_source(self):
        prisma_layers = ['Feição de Estudo/Sobreposição (padrão)', 'Feição de Estudo/Sobreposição', 'Sobreposição', 'Vértices', 'Linhas']
        field_data_source = self.layout.itemById('CD_FonteDados')

        all_layers = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
        print_layers = [value for value in all_layers if value not in prisma_layers]

        data_source = self.get_data_source(print_layers)

        text = ''
        for item in print_layers:
            if item != self.basemap:
                text_item = data_source[item][0] + " (" + data_source[item][1].split('/')[-1] +"), "
                if text_item not in text:
                    text += text_item

        text += self.basemap + " (2022)."
        self.rect_main_map = None
        field_data_source.setText(text)

    def get_data_source(self, layers_name):
        data_source = {}
        for name in layers_name:
            for x in self.operation_config['operation_config']['shp']:
                if name == x['nomeFantasiaCamada']:
                    data_source[str(name)] = [x['orgaoResponsavel'], x['periodosReferencia']]

            for x in self.operation_config['operation_config']['pg']:
                for x_layers in x['nomeFantasiaTabelasCamadas']:
                    if name == x_layers:
                        data_source[str(name)] = [x['orgaoResponsavel'], x['periodosReferencia']]

            for x in self.operation_config['operation_config']['required']:
                if 'nomeFantasiaCamada' in x:
                    if name == x['nomeFantasiaCamada']:
                        data_source[str(name)] = [x['orgaoResponsavel'], x['periodosReferencia']]
                else:
                    for x_layers in x['nomeFantasiaTabelasCamadas']:
                        if name == x_layers:
                            data_source[str(name)] = [x['orgaoResponsavel'], x['periodosReferencia']]

        return data_source

    def fill_observation(self, feature_input_gdp, layer_name):
        input = self.operation_config['input']

        overlay_area = self.layout.itemById('CD_Compl_Obs1')
        lot_area = self.layout.itemById('CD_Compl_Obs2')
        overlay_uniao = self.layout.itemById('CD_Compl_Obs3')
        overlay_uniao_area = self.layout.itemById('CD_Compl_Obs4')
        texto1 = self.layout.itemById('CD_Compl_Obs5')
        texto2 = self.layout.itemById('CD_Compl_Obs6')
        texto1.setText("")
        texto2.setText("")

        # Sobreposição com área de comparação
        if input.iloc[self.index_input][layer_name] == True:
            overlay_area.setText("Lote sobrepõe " + layer_name + ".")
        else:
            overlay_area.setText("Lote não sobrepõe " + layer_name + ".")

        # Área da feição
        format_value = f'{feature_input_gdp["areaLote"][0]:_.2f}'
        format_value = format_value.replace('.', ',').replace('_', '.')
        lot_area.setText("Área total do imóvel: " + str(format_value) + " m².")

        # Sobreposição com área da união
        if 'Área Homologada' in input and input.iloc[self.index_input]['Área Homologada'] > 0:
            overlay_uniao.setText("Lote sobrepõe Área Homologada da União.")
        else:
            overlay_uniao.setText("Lote não sobrepõe Área Homologada da União.")

        if 'Área Homologada' in feature_input_gdp:
            format_value = f'{feature_input_gdp.iloc[0]["Área Homologada"]:_.2f}'
            format_value = format_value.replace('.', ',').replace('_', '.')
            overlay_uniao_area.setText("Área de sobreposição com Área Homologada: " + str(format_value) + " m².")

    def add_template_to_project(self, template_dir):
        """
        Adiciona o template do layout ao projeto atual.
        @keyword template_dir: Variável armazena o local do layout.
        """
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
            symbol = QgsFillSymbol.createSimple(
                {'line_style': 'solid', 'line_color': 'black', 'color': 'gray', 'width_border': '0,35',
                 'style': 'solid'})

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

    def remove_layers(self):
        list_required = ['LPM Homologada', 'LTM Homologada', 'LLTM Homologada', 'LMEO Homologada', 'Área Homologada',
                         'LPM Não Homologada', 'LTM Não Homologada', 'Área Não Homologada', 'LLTM Não Homologada', 'LMEO Não Homologada',
                         self.basemap]
        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() not in list_required:
                QgsProject.instance().removeMapLayers([layer.id()])
