# -*- coding: utf-8 -*-
import os

from qgis.PyQt.QtWidgets import QApplication
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsRasterLayer, QgsVectorLayer, QgsFillSymbol, \
    QgsLineSymbol, QgsMarkerSymbol, QgsRectangle, QgsMapSettings, QgsLayoutSize, QgsUnitTypes, QgsLayoutExporter, \
    QgsPrintLayout, QgsReadWriteContext, QgsPalLayerSettings, QgsTextFormat, QgsVectorLayerSimpleLabeling
from qgis.PyQt.QtXml import QDomDocument
from qgis.utils import iface

from ..utils.utils import Utils
from ..settings.env_tools import EnvTools
from ..analysis.overlay_analysis import OverlayAnalisys
from .linestring_required import LinestringRequired

import geopandas as gpd
from shapely.geometry import Polygon, Point, LineString
from PyPDF2 import PdfFileReader, PdfFileMerger
from datetime import datetime
from .overlay_report_linestrings import OverlayReportLinestrings

class Linestrings():
    def __init__(self, operation_config):
        self.operation_config = operation_config

        self.layout = None
        self.atlas = None
        self.index_input = None
        self.time = None
        self.lr = LinestringRequired(self.operation_config)

        self.gpd_area_homologada = []
        self.rect_main_map = None
        self.overlay_report = OverlayReportLinestrings()

        self.utils = Utils()

        self.layers = []
        self.root = QgsProject.instance().layerTreeRoot()

    def comparasion_between_linestrings(self, input, input_standard, area, gdf_required, index_1, index_2, atlas, layout, index_input):
        self.atlas = atlas
        self.layout = layout

        input = self.calculation_required(input, gdf_required)
        # Extrai vértices da linha que está sendo comparada
        gdf_point_input = self.explode_input(input)
        # Cálculos de área e centroid da feição de input
        input.loc[0, 'areaLote'] = input.iloc[0]['geometry'].length
        input.loc[0, 'ctr_lat'] = input.iloc[0]['geometry'].centroid.y
        input.loc[0, 'ctr_long'] = input.iloc[0]['geometry'].centroid.x

        if index_2 == None:
            input.loc[0, self.operation_config['operation_config']['shp'][index_1]['nomeFantasiaCamada']] = False
        else:
            input.loc[0, self.operation_config['operation_config']['pg'][index_1]['nomeFantasiaTabelasCamadas'][
                index_2]] = False

        # # Extrai vértices onde as linhas se interceptam
        interseption_points = input.unary_union.intersection(area.unary_union)

        coord_x = []
        coord_y = []
        gdf_interseption_points = []
        # Extrai latitude e longitude desses vértices (Será usado para gerar tabelas pdf)

        if not interseption_points.is_empty:
            if index_2 == None:
                input.loc[0, self.operation_config['operation_config']['shp'][index_1]['nomeFantasiaCamada']] = True
            else:
                input.loc[0, self.operation_config['operation_config']['pg'][index_1]['nomeFantasiaTabelasCamadas'][
                    index_2]] = True
            for coord in interseption_points:
                coord_x.append(coord.x)
                coord_y.append(coord.y)

            data = list(zip(coord_x, coord_y, interseption_points))
            gdf_interseption_points = gpd.GeoDataFrame(columns=['coord_x', 'coord_y', 'geometry'], data=data,
                                                       crs=input.crs)
            gdf_interseption_points = gdf_interseption_points.reset_index()

        # Pega o tempo em que o processamento da feição atual se inicia
        # Utilizado para gerar os nomes únicos na hora de exportar o PDF
        if index_input != self.index_input:
            self.index_input = index_input
            date_and_time = datetime.now()
            self.time = date_and_time.strftime('%Y-%m-%d_%H-%M-%S')
            self.overlay_report.handle_overlay_report(input, self.operation_config, self.time, index_1, index_2)
            # Gera o layout PDF com a área de entrada e áreas da união
            self.lr.linestring_required_layers(input, input_standard, gdf_point_input, self.gpd_area_homologada, self.index_input, self.time, self.atlas, self.layout)

        if not interseption_points.is_empty:
            if len(input_standard) > 0:
                self.handle_layers(input.iloc[[0]], input_standard.iloc[[0]], area,
                                   gdf_point_input, gdf_required, index_1, index_2)
            else:
                self.handle_layers(input.iloc[[0]], input_standard, area, gdf_point_input,
                                   gdf_required, index_1, index_2)

    def calculation_required(self, input, gdf_required):

        input = input.reset_index()

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
                area = area.to_crs(crs)
                area.set_crs(allow_override=True, crs=crs)

                # Soma da área de interseção feita com feição de input e atual área comparada
                # Essa soma é atribuida a uma nova coluna, identificada pelo nome da área comparada. Ex área quilombola: 108.4
                if self.operation_config['operation_config']['required'][index]['nome'] == 'Área união homologada':
                    self.gpd_area_homologada = gpd.overlay(input, area)

                if 'nomeFantasiaCamada' in self.operation_config['operation_config']['required'][index]:
                    if self.operation_config['operation_config']['required'][index][
                        "nomeFantasiaCamada"] == "Área Homologada" or \
                            self.operation_config['operation_config']['required'][index][
                                "nomeFantasiaCamada"] == "Área Não Homologada":
                        input.loc[0, self.operation_config['operation_config']['required'][index]['nomeFantasiaCamada']] = gpd.overlay(
                            input, area).length.sum()
                    else:
                        points = input.unary_union.intersection(area.unary_union)
                        if not points.is_empty:
                            input.loc[0, self.operation_config['operation_config']['required'][index][
                                'nomeFantasiaCamada']] = True
                        else:
                            input.loc[0, self.operation_config['operation_config']['required'][index][
                                'nomeFantasiaCamada']] = False



                else:
                    if self.operation_config['operation_config']['required'][index][
                        "nomeFantasiaTabelasCamadas"] == "Área Homologada" or \
                            self.operation_config['operation_config']['required'][index][
                                "nomeFantasiaTabelasCamadas"] == "Área Não Homologada":
                        input.loc[0, self.operation_config['operation_config']['required'][index][
                            'nomeFantasiaTabelasCamadas']] = gpd.overlay(
                            input, length).area.sum()
                    else:
                        points = input.unary_union.intersection(area.unary_union)
                        if not points.is_empty:
                            input.loc[0, self.operation_config['operation_config']['required'][index][
                                'nomeFantasiaTabelasCamadas']] = True
                        else:
                            input.loc[0, self.operation_config['operation_config']['required'][index][
                                'nomeFantasiaTabelasCamadas']] = False



            index += 1

        return input

    def explode_input(self, gdf_input):
        geometry = gdf_input.iloc[0]['geometry']

        geometry_points = []
        coord_x = []
        coord_y = []

        if geometry.type == 'LineString':
            all_coords = geometry.coords

            for coord in all_coords:
                geometry_points.append(Point(coord))
                coord_x.append(list(coord)[0])
                coord_y.append(list(coord)[1])

        if geometry.type == 'MultiLineString':
            all_coords = []
            for ea in geometry:
                all_coords.append(list(ea.coords))

            for polygon in all_coords:
                for coord in polygon:
                    geometry_points.append(Point(coord))
                    coord_x.append(list(coord)[0])
                    coord_y.append(list(coord)[1])

        data = list(zip(coord_x, coord_y, geometry_points))

        gdf_geometry_points = gpd.GeoDataFrame(columns=['coord_x', 'coord_y', 'geometry'], data=data, crs=gdf_input.crs)
        # Remover o último vértice, para não ficar dois pontos no mesmo lugar

        return gdf_geometry_points

    def handle_layers(self, feature_input_gdp, input_standard, feature_area, feature_gdf_interseption_points, gdf_required, index_1, index_2):
        """
        Carrega camadas já processadas no QGis para que posteriormente possam ser gerados os relatórios no formato PDF. Após gerar todas camadas necessárias,
        está função aciona outra função (export_pdf), que é responsável por gerar o layout PDF a partir das feições carregadas nesta função.

        @keyword feature_input_gdp: Feição que está sendo processada e será carregada para o QGis.
        @keyword input_standard: Feição padrão isto é, sem zona de proximidade (caso necessário), que está sendo processada e será carregada para o QGis.
        @keyword feature_area: Camada de comparação que está sendo processada.
        @keyword feature_gdf_interseption_points: Camada de interseção (caso exista) e será carregada para o QGis.
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
        if len(feature_gdf_interseption_points) > 0:
            show_qgis_gdf_interseption_points = QgsVectorLayer(feature_gdf_interseption_points.to_json(), "Interseções")
            show_qgis_gdf_interseption_points.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

            QgsProject.instance().addMapLayer(show_qgis_gdf_interseption_points, False)
            self.root.insertLayer(len(QgsProject.instance().layerTreeRoot().children()) - 1, show_qgis_gdf_interseption_points)

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

            symbol = self.get_feature_symbol(show_qgis_areas.geometryType(),
                                             self.operation_config['operation_config']['shp'][index_1][
                                                 'estiloCamadas'][
                                                 0])
            show_qgis_areas.renderer().setSymbol(symbol)
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

            symbol = self.get_feature_symbol(show_qgis_areas.geometryType(),
                                             self.operation_config['operation_config']['pg'][index_1][
                                                 'estiloTabelasCamadas'][index_2])
            show_qgis_areas.renderer().setSymbol(symbol)
            QgsProject.instance().addMapLayer(show_qgis_areas, False)
            self.root.insertLayer(len(QgsProject.instance().layerTreeRoot().children()) - 1, show_qgis_areas)

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

            elif layer.name() == 'LPM Homologada' or layer.name() == 'LTM Homologada' or layer.name() == 'LPM Não Homologada' or layer.name() == 'LTM Não Homologada':
                layers_situation_map.append(layer)

            elif layer.name() == 'OpenStreetMap':
                layers_localization_map.append(layer)
                layers_situation_map.append(layer)

            elif layer.name() == 'Interseções':
                qml_style_dir = os.path.join(os.path.dirname(__file__), 'static\Estilo_Vertice_P.qml')
                layer.loadNamedStyle(qml_style_dir)
                layer.triggerRepaint()

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
        self.rect_main_map = main_map.extent()

        # Tamanho do mapa no layout
        main_map.attemptResize(QgsLayoutSize(390, 277, QgsUnitTypes.LayoutMillimeters))

        self.export_pdf(feature_input_gdp, feature_gdf_interseption_points, index_1, index_2)

    def export_pdf(self, feature_input_gdp, feature_gdf_interseption_points, index_1, index_2):
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
        if index_2 == None:
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
        pdf_settings.dpi = 150

        if atlas.enabled():
            pdf_settings.rasterizeWholeImage = True
            QgsLayoutExporter.exportToPdf(atlas, pdf_path,
                                          settings=pdf_settings)

        self.merge_pdf(pdf_name)

    def merge_pdf(self, pdf_name):
        pdf_name = "_".join(pdf_name.split("_", 3)[:3])

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
        prisma_layers = ['Feição de Estudo/Sobreposição (padrão)', 'Feição de Estudo/Sobreposição', 'Interseções']
        field_data_source = self.layout.itemById('CD_FonteDados')

        all_layers = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
        print_layers = [value for value in all_layers if value not in prisma_layers]

        data_source = self.get_data_source(print_layers)

        text = ''
        for item in print_layers:
            if item != 'OpenStreetMap':
                text_item = data_source[item][0] + " (" + data_source[item][1] + "), "
                if text_item not in text:
                    text += text_item

        text += "Nominatim (2022)."
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
        lot_area.setText("Comprimento total da linha: " + str(format_value) + " metros em " + str(len(feature_input_gdp.explode())) + " segmentos.")

        # Sobreposição com área da união
        if input.iloc[self.index_input]['Área Homologada'] > 0:
            overlay_uniao.setText("Lote sobrepõe Área Homologada da União.")
        else:
            overlay_uniao.setText("Lote não sobrepõe Área Homologada da União.")

        if 'Área Homologada' in feature_input_gdp:
            format_value = f'{feature_input_gdp.iloc[0]["Área Homologada"]:_.2f}'
            format_value = format_value.replace('.', ',').replace('_', '.')

            if len(self.gpd_area_homologada) > 0:
                overlay_uniao_area.setText("Sobreposição Área Homologada: " + str(format_value) + " metros em " + str(
                    len(self.gpd_area_homologada.explode())) + " segmentos.")
            else:
                overlay_uniao_area.setText("Sobreposição Área Homologada: 0 metros em 0 segmentos.")

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
        list_required = ['LPM Homologada', 'LTM Homologada', 'Área Homologada', 'LPM Não Homologada',
                         'LTM Não Homologada', 'Área Não Homologada', 'OpenStreetMap']
        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() not in list_required:
                QgsProject.instance().removeMapLayers([layer.id()])
