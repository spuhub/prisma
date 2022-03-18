# -*- coding: utf-8 -*-
import os

from qgis.PyQt.QtWidgets import QApplication
from qgis.PyQt.QtGui import QFont
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsRasterLayer, QgsVectorLayer, QgsFillSymbol, \
    QgsLineSymbol, QgsMarkerSymbol, QgsRectangle, QgsMapSettings, QgsLayoutSize, QgsUnitTypes, QgsLayoutExporter, \
    QgsPrintLayout, QgsReadWriteContext, QgsPalLayerSettings, QgsTextFormat, QgsVectorLayerSimpleLabeling
from qgis.PyQt.QtXml import QDomDocument
from qgis.utils import iface

from ..utils.utils import Utils
from ..settings.env_tools import EnvTools
from ..analysis.overlay_analysis import OverlayAnalisys

import geopandas as gpd
import shapely.geometry

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
        self.required_layers_loaded = False

        # Adiciona o layout ao projeto atual
        template_dir = os.path.join(os.path.dirname(__file__), 'layouts\Planta_FolhaA3_Paisagem.qpt')
        self.add_template_to_project(template_dir)

        self.layout = None
        self.atlas = None
        self.layers = []

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
                gdf_input = self.calculation_required(input.iloc[[indexInput]], gdf_required)
                gdf_line_input = self.explode_layer_line(gdf_input)
                # Caso input_standard maior que 0, significa que o usuário inseriu uma área de proximidade
                if len(input_standard) > 0:
                    self.calculation_shp(gdf_input, gdf_line_input, input_standard.iloc[[indexInput]], gdf_selected_shp, gdf_required)
                    self.calculation_db(gdf_input, gdf_line_input, input_standard.iloc[[indexInput]], gdf_selected_db, gdf_required)
                else:
                    self.calculation_shp(gdf_input, gdf_line_input, input_standard, gdf_selected_shp, gdf_required)
                    self.calculation_db(gdf_input, gdf_line_input, input_standard, gdf_selected_db, gdf_required)
            atual_progress += interval_progress
            self.progress_bar.setValue(atual_progress)

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
            for base_name in list_required:
                if base['nomeFantasiaTabelasCamadas'] == base_name:
                    self.operation_config['operation_config']['required'].append(base)
                    gdf_required.append(gdf_selected_db.pop(index - shift))
                    shift += 1
                else:
                    new_operation_config.append(base)

        self.operation_config['operation_config']['pg'] = new_operation_config
        return gdf_required, gdf_selected_shp, gdf_selected_db

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
            area = area.to_crs(crs)
            area.set_crs(allow_override=True, crs=crs)

            # Soma da área de interseção feita com feição de input e atual área comparada
            # Essa soma é atribuida a uma nova coluna, identificada pelo nome da área comparada. Ex área quilombola: 108.4
            if 'nomeFantasiaCamada' in self.operation_config['operation_config']['required'][index]:
                input.loc[0, self.operation_config['operation_config']['required'][index]['nomeFantasiaCamada']] = gpd.overlay(
                    input, area).area.sum()
            else:
                input.loc[0, self.operation_config['operation_config']['required'][index][
                    'nomeFantasiaTabelasCamadas']] = gpd.overlay(
                    input, area).area.sum()

            index += 1

        return input

    def explode_layer_line(self, gdf_input):
        line_segs = gpd.GeoSeries(
            gdf_input["geometry"]
                .apply(
                lambda g: [g]
                if isinstance(g, shapely.geometry.Polygon)
                else [p for p in g.geoms]
            )
                .apply(
                lambda l: [
                    shapely.geometry.LineString([c1, c2])
                    for p in l
                    for c1, c2 in zip(p.exterior.coords, list(p.exterior.coords)[1:])
                ]
            )
                .explode()
        )

        line_segs = gpd.GeoDataFrame(geometry=gpd.GeoSeries(line_segs), crs = gdf_input.crs)
        line_segs = line_segs.set_geometry('geometry')

        line_segs['length_line'] = None
        line_segs = line_segs.reset_index()

        for index, row in line_segs.iterrows():
            round_number = line_segs.iloc[index]["geometry"].length
            format_value = f'{round_number:_.2f}'
            format_value = format_value.replace('.', ',').replace('_', '.')

            line_segs.loc[index, 'length_line'] = str(format_value) + " m²"

        return line_segs

    def calculation_shp(self, input, gdf_line_input, input_standard, gdf_selected_shp, gdf_required):
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

        if 'aproximacao' in self.operation_config['operation_config']:
            input = self.utils.add_input_approximation_projected(input, self.operation_config['operation_config'][
                'aproximacao'])

        if len(input_standard) > 0:
            input_standard = input_standard.to_crs(crs)
            input_standard.set_crs(crs, allow_override=True)

        # Cálculos de área e centroid da feição de input
        input.loc[0, 'areaLote'] = input.iloc[0]['geometry'].area
        input.loc[0, 'ctr_lat'] = input.iloc[0]['geometry'].centroid.y
        input.loc[0, 'ctr_long'] = input.iloc[0]['geometry'].centroid.x

        index = 0
        # Compara a feição de entrada com todas as áreas de comparação shp selecionadas pelo usuário
        for index, area in enumerate(gdf_selected_shp):
            intersection = []
            area = area.to_crs(crs)
            area.set_crs(allow_override=True, crs=crs)
            if 'aproximacao' in self.operation_config['operation_config']['shp'][index]:
                area = self.utils.add_input_approximation_projected(area, self.operation_config['operation_config']['shp'][index]['aproximacao'][0])

            # Soma da área de interseção feita com feição de input e atual área comparada
            # Essa soma é atribuida a uma nova coluna, identificada pelo nome da área comparada. Ex área quilombola: 108.4
            input.loc[0, self.operation_config['operation_config']['shp'][index]['nomeFantasiaCamada']] = gpd.overlay(
                input, area).area.sum()

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

            intersection = gpd.GeoDataFrame(data, crs=input.crs)

            # Gera planta pdf somente quando acontece sobreposição
            if len(intersection) > 0:
                intersection.set_crs(allow_override=True, crs=crs)

                if len(input_standard) > 0:
                    self.handle_layers(input.iloc[[0]], gdf_line_input, input_standard.iloc[[0]], area, intersection, gdf_required, index, None)
                else:
                    self.handle_layers(input.iloc[[0]], gdf_line_input, input_standard, area, intersection, gdf_required, index, None)

            index += 1

    def calculation_db(self, input, gdf_line_input, input_standard, gdf_selected_db, gdf_required):
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

        if 'aproximacao' in self.operation_config['operation_config']:
            input = self.utils.add_input_approximation_projected(input, self.operation_config['operation_config'][
                'aproximacao'])

        # Cálculos de área de input e centroid feição de entrada
        input.loc[0, 'areaLote'] = input.iloc[0]['geometry'].area
        input.loc[0, 'ctr_lat'] = input.iloc[0]['geometry'].centroid.y
        input.loc[0, 'ctr_long'] = input.iloc[0]['geometry'].centroid.x

        index_db = 0
        # Compara a feição de entrada com todas as áreas de comparação db selecionadas pelo usuário
        for db in gdf_selected_db:
            index_layer = 0
            for area in db:
                # area.crs = {'init':'epsg:4674'}
                area = area.to_crs(crs)
                area.set_crs(allow_override=True, crs=crs)

                # Soma da área de interseção feita com feição de input e atual área comparada
                # Essa soma é atribuida a uma nova coluna, identificada pelo nome da área comparada. Ex área quilombola: 108.4
                input.loc[0, self.operation_config['operation_config']['pg'][index_db]['nomeFantasiaTabelasCamadas'][
                    index_layer]] = gpd.overlay(input, area).area.sum()

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

                intersection = gpd.GeoDataFrame(data, crs=input.crs)

                # Gera planta pdf somente quando ,acontece sobreposição
                if len(intersection) > 0:
                    intersection.set_crs(allow_override=True, crs=crs)

                    if len(input_standard) > 0:
                        self.handle_layers(input.iloc[[0]], gdf_line_input, input_standard.iloc[[0]], area, intersection, gdf_required, index_db,
                                        index_layer)
                    else:
                        self.handle_layers(input.iloc[[0]], gdf_line_input, input_standard, area, intersection, gdf_required, index_db, index_layer)

                index_layer += 1
            index_db += 1

    def handle_layers(self, feature_input_gdp, gdf_line_input, input_standard, feature_area, feature_intersection, gdf_required, index_1, index_2):
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

        if self.required_layers_loaded == False:
            self.load_required_layers(gdf_required, crs)
            self.required_layers_loaded = True

        self.remove_layers()

        # len(QgsProject.instance().layerTreeRoot().children()) # usar depois
        # self.root.insertLayer(0, self.root.layerOrder()[3]) # usar depois

        # self.root.insertLayer(len(QgsProject.instance().layerTreeRoot().children()) - 2, )

        # Carrega as áreas de intersecção no Qgis
        if len(feature_intersection) > 0:
            show_qgis_intersection = QgsVectorLayer(feature_intersection.to_json(), "Sobreposição")
            show_qgis_intersection.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

            symbol = QgsFillSymbol.createSimple(
                {'line_style': 'solid', 'line_color': 'black', 'color': 'yellow', 'width_border': '0,35',
                 'style': 'solid'})
            show_qgis_intersection.renderer().setSymbol(symbol)
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

        # Camada de cotas
        show_qgis_quota = QgsVectorLayer(gdf_line_input.to_json(), "Linhas")
        show_qgis_quota.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

        symbol = self.get_feature_symbol(show_qgis_quota.geometryType(), {
                "line_style": "solid",
                "line_color": "black",
                "width_border": "0.35",
                "style": "solid",
                "color": "red"
            })
        show_qgis_quota.renderer().setSymbol(symbol)
        QgsProject.instance().addMapLayer(show_qgis_quota)

        QApplication.instance().processEvents()

        layer = iface.activeLayer()
        pal_layer = QgsPalLayerSettings()
        text_format = QgsTextFormat()

        text_format.setFont(QFont("Arial", 10))
        text_format.setSize(10)

        pal_layer.setFormat(text_format)
        pal_layer.fieldName = "length_line"
        pal_layer.isExpression = True
        pal_layer.enabled = True
        pal_layer.placement = QgsPalLayerSettings.Line
        labels = QgsVectorLayerSimpleLabeling(pal_layer)
        layer.setLabeling(labels)
        layer.setLabelsEnabled(True)
        layer.triggerRepaint()

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

        # Configurações no QGis para gerar os relatórios PDF
        ms = QgsMapSettings()
        ms.setLayers([self.layers])
        rect = QgsRectangle(ms.fullExtent())

        main_map = self.layout.itemById('Planta_Principal')

        ms.setExtent(rect)
        main_map.zoomToExtent(rect)

        iface.mapCanvas().refresh()
        main_map.refresh()

        # Tamanho do mapa no layout
        main_map.attemptResize(QgsLayoutSize(390, 277, QgsUnitTypes.LayoutMillimeters))

        self.export_pdf(feature_input_gdp, index_1, index_2)

    def load_required_layers(self, gdf_required, crs):
        # Carrega camada mundial do OpenStreetMap
        tms = 'type=xyz&url=http://a.tile.openstreetmap.org/{z}/{x}/{y}.png'
        layer = QgsRasterLayer(tms, 'OpenStreetMap', 'wms')
        QgsProject.instance().addMapLayer(layer)
        QApplication.instance().processEvents()

        index = 0
        for area in gdf_required:
            area = area.to_crs(crs)
            area = area.set_crs(crs, allow_override = True)

            show_qgis_areas = None
            if 'nomeFantasiaCamada' in self.operation_config['operation_config']['required'][index]:
                show_qgis_areas = QgsVectorLayer(area.to_json(),
                                             self.operation_config['operation_config']['required'][index][
                                                 'nomeFantasiaCamada'])
            else:
                show_qgis_areas = QgsVectorLayer(area.to_json(),
                                                 self.operation_config['operation_config']['required'][index][
                                                     'nomeFantasiaTabelasCamadas'][0])

            show_qgis_areas.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

            symbol = self.get_feature_symbol(show_qgis_areas.geometryType(),
                                             self.operation_config['operation_config']['required'][index]['estiloCamadas'][
                                                 0])
            show_qgis_areas.renderer().setSymbol(symbol)
            QgsProject.instance().addMapLayer(show_qgis_areas)

            index += 1

    def export_pdf(self, feature_input_gdp, index_1, index_2):
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

        if index_2 == None:
            pdf_name = str(feature_input_gdp.iloc[0]['logradouro']) + '_' + str(
                self.operation_config['operation_config']['shp'][index_1]['nomeFantasiaCamada']) + '.pdf'
        else:
            pdf_name = str(feature_input_gdp.iloc[0]['logradouro']) + '_' + str(
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

    QApplication.instance().processEvents()

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
        if geometry_type == 0:
            symbol = QgsMarkerSymbol.createSimple(style)
        # Line String
        if geometry_type == 1:
            symbol = QgsLineSymbol.createSimple(style)
        # Polígono
        elif geometry_type == 2:
            symbol = QgsFillSymbol.createSimple(style)

        return symbol

    def remove_layers(self):
        list_required = ['LPM Homologada', 'LTM Homologada', 'Área Homologada', 'LPM Não Homologada',
                         'LTM Não Homologada', 'Área Não Homologada', 'OpenStreetMap']
        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() not in list_required:
                QgsProject.instance().removeMapLayers([layer.id()])
