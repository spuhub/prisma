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
from .polygons import Polygons
from .linestrings import Linestrings

import geopandas as gpd
from shapely.geometry import Polygon, Point, LineString

class LayoutManager():
    """Classe responsável por fazer a manipulação do Layout de impressão. Contém métodos para fazer o controle das feições carregadas para impressão,
    manipular textos e também algumas operações com dados que serão plotados ou utilizados para gerar relatórios PDF.

    @ivar atlas: Variável que armazena o atlas do layout para geração de plantas PDF.
    @ivar epsg_shp_dir: Diretório do shapefile para gerar dinamicamente os EPSG's (Comtém as Zonas UTM).
    @ivar layers: Utilizada para salvar a camada de input, já processada e projetada no QGIS.
    @ivar layout: Variável que armazena o layout para geração de plantas PDF.
    @ivar overlay_analysis: Variável utilizada para importar a classe presente em prisma/analysis/overlay_analysis.py.
    @ivar progress_bar: Variável de controle da barra de progresso do processamento para geração de plantas PDF.
    @ivar operation_config: Dicionário que armazena configurações de operação, como por exemplo: dado de input, bases de dados selecionadas para comparação, busca por ponto, shapefile, etc...
    @ivar utils: Variável conténdo classe presentem em prisma/utils/utils.py
    """

    def __init__(self, operation_config, progress_bar):
        """Método construtor da classe.

        @keyword operation_config: Dicionário que armazena configurações de operação, como por exemplo: dado de input, bases de dados selecionadas para comparação, busca por ponto, shapefile, etc...
        @keyword progress_bar: Variável de controle da barra de progresso do processamento para geração de relatórios PDF.
        """

        self.overlay_analysis = OverlayAnalisys()
        self.root = QgsProject.instance().layerTreeRoot()

        self.operation_config = operation_config
        self.progress_bar = progress_bar
        self.utils = Utils()
        self.index_input = None

        # Adiciona o layout ao projeto atual
        template_dir = os.path.join(os.path.dirname(__file__), 'layouts\Planta_FolhaA3_Paisagem.qpt')
        self.add_template_to_project(template_dir)

        self.layout = None
        self.atlas = None
        self.layers = []

        self.polygons = Polygons(self.operation_config)
        self.linestrings = Linestrings(self.operation_config)

        # Diretório do shapefile para gerar dinamicamente os EPSG's
        self.epsg_shp_dir = os.path.join(os.path.dirname(__file__), '..\shapefiles\Zonas_UTM_BR-EPSG4326.shp')

    def pdf_generator(self):
        """Função onde se inicia a geração de PDF. A função chama funções de calculo de sobreposição de forma individual para
            cada feição de input. Ainda nesta função é extraida a zona UTM das feições de input e controle da barra de progresso."""
        # Armazena na variável o layout que acabou de ser adicionado ao projeto, permitindo a manipulação do mesmo
        self.layout = QgsProject.instance().layoutManager().layoutByName("Planta_FolhaA3_Paisagem")
        self.atlas = self.layout.atlas()

        input = self.operation_config['input_standard']
        input_geographic = self.operation_config['input']

        input = input.to_crs(crs=4326)

        input_standard = self.operation_config['input_standard']
        gdf_selected_shp = self.operation_config['gdf_selected_shp']
        gdf_selected_db = self.operation_config['gdf_selected_db']
        gdf_required, gdf_selected_shp, gdf_selected_db = self.get_required_layers(gdf_selected_shp, gdf_selected_db)

        # Verifica em qual Zona UTM cada uma das feições está inserida
        input['crs_feature'] = self.overlay_analysis.get_utm_crs(input_geographic, self.epsg_shp_dir)

        # Barra de progresso
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setHidden(False)
        interval_progress = 100 / len(input)
        atual_progress = 0
        self.progress_bar.setValue(atual_progress)

        input['LPM Homologada'] = 0
        input['LTM Homologada'] = 0
        input['Área Homologada'] = 0
        input['LPM Não Homologada'] = 0
        input['LTM Não Homologada'] = 0
        input['Área Não Homologada'] = 0

        # Remove camadas já impressas
        QgsProject.instance().removeAllMapLayers()
        QApplication.instance().processEvents()

        # Os cálculos de área, centroide, interseções são feitos aqui, de forma individual para cada feição
        # do shp de entrada. Após realizar os cálculos, as funções calculation_shp e calculation_db
        # chamam a função de exportar pdf
        for indexInput, rowInput in input.iterrows():
            self.index_input = indexInput
            # Caso rowInput['crs_feature'] for igual a False, significa que a feição faz parte de dois ou mais zonas
            # portanto, não é processado
            if rowInput['crs_feature'] != False:
                if indexInput == 0:
                    self.load_required_layers(gdf_required, rowInput['crs_feature'])
                else:
                    # Caso feição atual tenha crs diferente, remove todas camadas e gera novamente
                    if input.iloc[indexInput-1]['crs_feature'] != rowInput['crs_feature']:
                        QgsProject.instance().removeAllMapLayers()
                        QApplication.instance().processEvents()
                        self.load_required_layers(gdf_required, rowInput['crs_feature'])

                gdf_input = self.get_feature_with_crs(input.iloc[[indexInput]])
                # Caso input_standard maior que 0, significa que o usuário inseriu uma área de proximidade
                if len(input_standard) > 0:
                    self.calculation_shp(gdf_input, input_standard.iloc[[indexInput]], gdf_selected_shp, gdf_required)
                    self.calculation_db(gdf_input, input_standard.iloc[[indexInput]], gdf_selected_db, gdf_required)
                else:
                    self.calculation_shp(gdf_input, input_standard, gdf_selected_shp, gdf_required)
                    self.calculation_db(gdf_input, input_standard, gdf_selected_db, gdf_required)
            atual_progress += interval_progress
            self.progress_bar.setValue(atual_progress)

    def get_feature_with_crs(self, input):
        crs = 'EPSG:' + str(input.iloc[0]['crs_feature'])

        input = input.to_crs(crs)
        input.set_crs(crs, allow_override=True)

        return input

    def get_required_layers(self, gdf_selected_shp, gdf_selected_db):
        """
        Extrai as camadas obrigatórias das bases de dados shp e db e do dicionário de configuração.
        """
        self.operation_config['operation_config']['required'] = []
        new_operation_config = []
        gdf_required = []
        list_required = ['LPM Homologada', 'LTM Homologada', 'Área Homologada', 'LPM Não Homologada', 'LTM Não Homologada', 'Área Não Homologada']

        shift = 0
        for index, base in enumerate(self.operation_config['operation_config']['shp']):
            if base['nomeFantasiaCamada'] in list_required:
                self.operation_config['operation_config']['required'].append(base)
                gdf_required.append(gdf_selected_shp.pop(index - shift))
                shift += 1
            else:
                new_operation_config.append(base)

        self.operation_config['operation_config']['shp'] = new_operation_config

        new_operation_config = []
        shift = 0
        for index, base in enumerate(self.operation_config['operation_config']['pg']):
            for name in base['nomeFantasiaTabelasCamadas']:
                if name in list_required:
                    self.operation_config['operation_config']['required'].append(base)
                    gdf_required.append(gdf_selected_db.pop(index - shift))
                    shift += 1
                else:
                    new_operation_config.append(base)

        self.operation_config['operation_config']['pg'] = new_operation_config
        return gdf_required, gdf_selected_shp, gdf_selected_db

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
        # Remover o último vértice, para não ficar dois pontos no mesmo lugar
        gdf_geometry_points = gdf_geometry_points[:-1]

        gdf_geometry_lines = gpd.GeoDataFrame(geometry=geometry_lines, crs=gdf_input.crs)

        return gdf_geometry_points, gdf_geometry_lines

    def calculation_shp(self, input, input_standard, gdf_selected_shp, gdf_required):
        """
        Função compara a feição de input passada como parâmetro com bases de dados shapefiles selecionados. Para cada área de comparação
        comparada com a feição de input, chama a função handle_layers, responsável por gerar as camadas no QGIS.

        @keyword input: Feição ou shapefile de input, caso possua zona de proximidade inserida pelo usuário, a mesma será armazenado nesta variável.
        @keyword input_standard: Feição ou shapefile de input padrão isto é, sem zona de proximidade (caso necessário).
        @keyword gdf_selected_shp: Shapefiles selecionados para comparação com a área de input.
        """
        crs = 'EPSG:' + str(input.iloc[0]['crs_feature'])

        input = input.to_crs(crs)
        input.set_crs(crs, allow_override=True)

        if len(input_standard) > 0:
            input_standard = input_standard.to_crs(crs)
            input_standard.set_crs(crs, allow_override=True)

        # Compara a feição de entrada com todas as áreas de comparação shp selecionadas pelo usuário
        for index, area in enumerate(gdf_selected_shp):
            area = area.to_crs(crs)
            area.set_crs(allow_override=True, crs=crs)

            if 'aproximacao' in self.operation_config['operation_config']['shp'][index]:
                area = self.utils.add_input_approximation_projected(area, self.operation_config['operation_config']['shp'][index]['aproximacao'][0])

            if len(area) > 0:
                if input.iloc[0]['geometry'].type in ['Polygon', 'MultiPolygon'] and area.iloc[0][
                    'geometry'].type in ['Polygon', 'MultiPolygon']:
                    self.polygons.comparasion_between_polygons(input, input_standard, area, gdf_required, index, None,
                                                               self.atlas, self.layout, self.index_input)

                elif input.iloc[0]['geometry'].type in ['LineString', 'MultiLineString'] and area.iloc[0][
                    'geometry'].type in ['LineString', 'MultiLineString']:
                    self.linestrings.comparasion_between_linestrings(input, input_standard, area, gdf_required, index, None,
                                                               self.atlas, self.layout, self.index_input)

    def calculation_db(self, input, input_standard, gdf_selected_db, gdf_required):
        """
        Função compara a feição de input passada como parâmetro com bases de dados oriundas de bancos de dados. Para cada área de comparação
        comparada com a feição de input, chama a função handle_layers, responsável por gerar as camadas no QGIS.

        @keyword input: Feição ou shapefile de input, caso possua zona de proximidade inserida pelo usuário, a mesma será armazenado nesta variável.
        @keyword input_standard: Feição ou shapefile de input padrão isto é, sem zona de proximidade (caso necessário).
        @keyword gdf_selected_db: Bases de dados de banco(s) de dado selecionados para comparação com a área de input.
        """
        intersection = []

        crs = 'EPSG:' + str(input.iloc[0]['crs_feature'])

        input = input.to_crs(crs)
        input.set_crs(crs, allow_override=True)

        index_db = 0
        # Compara a feição de entrada com todas as áreas de comparação db selecionadas pelo usuário
        for db in gdf_selected_db:
            index_layer = 0
            for area in db:
                # area.crs = {'init':'epsg:4674'}
                area = area.to_crs(crs)
                area.set_crs(allow_override=True, crs=crs)
                if len(area) > 0:
                    if input.iloc[0]['geometry'].type in ['Polygon', 'MultiPolygon'] and area.iloc[0][
                        'geometry'].type in ['Polygon', 'MultiPolygon']:
                        self.polygons.comparasion_between_polygons(input, input_standard, area, gdf_required, index_db,
                                                                   index_layer, self.atlas, self.layout, self.index_input)

                    elif input.iloc[0]['geometry'].type in ['Linestring', 'MultiLinestring'] and area.iloc[0][
                        'geometry'].type in ['Linestring', 'MultiLinestring']:
                        self.linestrings.comparasion_between_linestrings(input, input_standard, area, gdf_required, index_db,
                                                                   index_layer, self.atlas, self.layout, self.index_input)
                index_layer += 1
            index_db += 1

    def load_required_layers(self, gdf_required, crs):
        # Carrega camada mundial do OpenStreetMap
        tms = 'type=xyz&url=http://a.tile.openstreetmap.org/{z}/{x}/{y}.png'
        layer = QgsRasterLayer(tms, 'OpenStreetMap', 'wms')
        QgsProject.instance().addMapLayer(layer)
        QApplication.instance().processEvents()

        index = 0
        for area in gdf_required:
            if len(area) > 0:
                if isinstance(area, list):
                    area = area[0].to_crs(crs)
                else:
                    area = area.to_crs(crs)

                area = area.set_crs(crs, allow_override = True)

                if len(area) > 0:
                    show_qgis_areas = None
                    symbol = None
                    if 'nomeFantasiaCamada' in self.operation_config['operation_config']['required'][index]:
                        show_qgis_areas = QgsVectorLayer(area.to_json(),
                                                     self.operation_config['operation_config']['required'][index][
                                                         'nomeFantasiaCamada'])
                        symbol = self.get_feature_symbol(show_qgis_areas.geometryType(),
                                                         self.operation_config['operation_config']['required'][index][
                                                             'estiloCamadas'][
                                                             0])
                    else:
                        if 'geom' in area:
                            area = area.drop(columns=['geom'])
                        show_qgis_areas = QgsVectorLayer(area.to_json(),
                                                         self.operation_config['operation_config']['required'][index][
                                                             'nomeFantasiaTabelasCamadas'][0])
                        symbol = self.get_feature_symbol(show_qgis_areas.geometryType(),
                                                         self.operation_config['operation_config']['required'][index][
                                                             'estiloTabelasCamadas'][
                                                             0])

                    show_qgis_areas.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))
                    show_qgis_areas.renderer().setSymbol(symbol)
                    QgsProject.instance().addMapLayer(show_qgis_areas)

            index += 1

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
