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


class PolygonRequired():
    def __init__(self, operation_config):
        self.operation_config = operation_config

        self.layout = None
        self.atlas = None
        self.index_input = None

        self.utils = Utils()
        self.time = None

        self.layers = []
        self.rect_main_map = None
        self.root = QgsProject.instance().layerTreeRoot()

    def polygon_required_layers(self, input, input_standard, gdf_line_input, gdf_point_input, index_input, time, atlas, layout):
        self.time = time
        self.index_input = index_input
        self.atlas = atlas
        self.layout = layout

        if len(input_standard) > 0:
            self.handle_layers(input.iloc[[0]], gdf_line_input, gdf_point_input, input_standard.iloc[[0]])
        else:
            self.handle_layers(input.iloc[[0]], gdf_line_input, gdf_point_input, input_standard)

    def handle_layers(self, feature_input_gdp, gdf_line_input, gdf_point_input, input_standard):
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

        # Carrega a área padrão no QGis, sem área de aproximação (caso necessário)
        if 'aproximacao' in self.operation_config['operation_config']:
            # Carrega camada de input no QGis (Caso usuário tenha inserido como entrada, a área de aproximação está nesta camada)
            show_qgis_input = QgsVectorLayer(feature_input_gdp.to_json(), "Feição de Estudo/Sobreposição")
            show_qgis_input.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

            symbol = self.get_input_symbol(show_qgis_input.geometryType())
            show_qgis_input.renderer().setSymbol(symbol)
            QgsProject.instance().addMapLayer(show_qgis_input, False)
            self.root.insertLayer(len(QgsProject.instance().layerTreeRoot().children()) - 1, show_qgis_input)

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

        # Camada de cotas
        show_qgis_quota = QgsVectorLayer(gdf_line_input.to_json(), "Linhas")
        show_qgis_quota.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

        QgsProject.instance().addMapLayer(show_qgis_quota, False)
        self.root.insertLayer(0, show_qgis_quota)

        # Camada de vértices
        show_qgis_vertices = QgsVectorLayer(gdf_point_input.to_json(), "Vértices")
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

            elif layer.name() == 'LPM Homologada' or layer.name() == 'LTM Homologada' or layer.name() == 'LPM Não Homologada' or layer.name() == 'LTM Não Homologada':
                layers_situation_map.append(layer)

            elif layer.name() == 'OpenStreetMap':
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

        self.export_pdf(feature_input_gdp)

    def export_pdf(self, feature_input_gdp):
        """
        Função responsável carregar o layout de impressão e por gerar os arquivos PDF.

        @keyword feature_input_gdp: Feição de input comparada
        @keyword index_1: Variável utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar informções como estilização ou nome da camada.
        @keyword index_2: Variável utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar informções como estilização ou nome da camada.
        """
        # Manipulação dos textos do layout
        self.handle_text(feature_input_gdp)

        if 'logradouro' not in feature_input_gdp:
            feature_input_gdp['logradouro'] = "Ponto por Endereço ou Coordenada"

        pdf_name = str(feature_input_gdp.iloc[0]['logradouro']) + '_' + str(self.time) + '_AreasUniao.pdf'
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
        print(pdf_name)
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


    def handle_text(self, feature_input_gdp):
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
        layer_name = "Áreas da União"
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
            if item != 'OpenStreetMap':
                text_item = data_source[item][0] + " (" + data_source[item][1] +"), "
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

        overlay_area.setText("")

        # Área da feição
        format_value = f'{feature_input_gdp["areaLote"][0]:_.2f}'
        format_value = format_value.replace('.', ',').replace('_', '.')
        lot_area.setText("Área total do imóvel: " + str(format_value) + " m².")

        # Sobreposição com área da união
        if input.iloc[self.index_input]['Área Homologada'] > 0:
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
        list_required = ['LPM Homologada', 'LTM Homologada', 'Área Homologada', 'LPM Não Homologada',
                         'LTM Não Homologada', 'Área Não Homologada', 'OpenStreetMap']
        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() not in list_required:
                QgsProject.instance().removeMapLayers([layer.id()])
