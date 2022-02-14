import os

from qgis.PyQt.QtWidgets import QApplication
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsRasterLayer, QgsVectorLayer, QgsFillSymbol, QgsLineSymbol, QgsMarkerSymbol, QgsRectangle, QgsMapSettings, QgsLayoutSize, QgsUnitTypes, QgsLayoutExporter, QgsPrintLayout, QgsReadWriteContext
from qgis.PyQt.QtXml import QDomDocument
from qgis.utils import iface

from ..utils.utils import Utils
from ..settings.env_tools import EnvTools
from ..analysis.overlay_analysis import OverlayAnalisys

import geopandas as gpd

class LayoutManager():
    def __init__(self, result, progress_bar):
        super().__init__()
        self.overlay_analysis = OverlayAnalisys()

        self.result = result
        self.progress_bar = progress_bar
        self.utils = Utils()

        # Adiciona o layout ao projeto atual
        template_dir = os.path.join(os.path.dirname(__file__), 'layouts\Planta_FolhaA3_Paisagem.qpt')
        self.add_template_to_project(template_dir)

        self.layout = None
        self.atlas = None
        self.layers = []

        # Diretório do shapefile para gerar dinamicamente os EPSG's
        self.epsg_shp_dir = os.path.join(os.path.dirname(__file__), '..\shapefiles\Zonas_UTM_BR-EPSG4326.shp')

    """
    Função onde se inicia a geração de PDF. A função chama funções de calculo de sobreposição de forma individual para 
    cada feição de input. Ainda nesta função é extraida a zona UTM das feições de input e controle da barra de progresso.
    """
    def pdf_generator(self):
        # Armazena na variável o layout que acabou de ser adicionado ao projeto, permitindo a manipulação do mesmo
        self.layout = QgsProject.instance().layoutManager().layoutByName("Planta_FolhaA3_Paisagem")
        self.atlas = self.layout.atlas()

        input = self.result['input_standard']
        input_geographic = self.result['input']
        input = input.to_crs(crs=4326)

        input_standard = self.result['input_standard']
        gdf_selected_shp = self.result['gdf_selected_shp']
        gdf_selected_db = self.result['gdf_selected_db']

        # Verifica em qual Zona UTM cada uma das feições está inserida
        input['crs_feature'] = self.overlay_analysis.get_utm_crs(input_geographic, self.epsg_shp_dir)

        # Barra de progresso
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setHidden(False)
        interval_progress = 100 / len(input)
        atual_progress = 0
        self.progress_bar.setValue(atual_progress)
        # Os cálculos de área, centroide, interseções são feitos aqui, de forma individual para cada feição
        # do shp de entrada. Após realizar os cálculos, as funções calculation_shp e calculation_db
        # chamam a função de exportar pdf
        for indexInput, rowInput in input.iterrows():
            # Caso rowInput['crs_feature'] for igual a False, significa que a feição faz parte de dois ou mais zonas
            # portanto, não é processado
            if rowInput['crs_feature'] != False:
                # Caso input_standard maior que 0, significa que o usuário inseriu uma área de proximidade
                if len(input_standard) > 0:
                    self.calculation_shp(input.iloc[[indexInput]], input_standard.iloc[[indexInput]],  gdf_selected_shp)
                    self.calculation_db(input.iloc[[indexInput]], input_standard.iloc[[indexInput]], gdf_selected_db)
                else:
                    self.calculation_shp(input.iloc[[indexInput]], input_standard, gdf_selected_shp)
                    self.calculation_db(input.iloc[[indexInput]], input_standard, gdf_selected_db)
            atual_progress += interval_progress
            self.progress_bar.setValue(atual_progress)

    """
    Função compara a feição de input passada como parâmetro com bases de dados shapefiles selecionados.
    :parâmetro input: Feição ou shapefile de input, caso possua zona de proximidade inserida pelo usuário, a mesma será armazenado nesta variável.
    :parâmetro input_standard: Feição ou shapefile de input padrão isto é, sem zona de proximidade (caso necessário).
    :parâmetro gdf_selected_shp: Shapefiles selecionados para comparação com a área de input.
    """
    def calculation_shp(self, input, input_standard, gdf_selected_shp):
        input = input.reset_index()

        crs = 'EPSG:' + str(input.iloc[0]['crs_feature'])

        input = input.to_crs(crs)
        input.set_crs(crs, allow_override=True)

        if 'aproximacao' in self.result['operation_config']:
            input = self.utils.add_input_approximation_projected(input, self.result['operation_config']['aproximacao'])

        if len(input_standard) > 0:
            input_standard = input_standard.to_crs(crs)
            input_standard.set_crs(crs, allow_override=True)

        # Cálculos de área e centroid da feição de input
        input.loc[0, 'areaLote'] = input.iloc[0]['geometry'].area
        input.loc[0, 'ctr_lat'] = input.iloc[0]['geometry'].centroid.y
        input.loc[0, 'ctr_long'] = input.iloc[0]['geometry'].centroid.x

        index = 0
        # Compara a feição de entrada com todas as áreas de comparação shp selecionadas pelo usuário
        for area in gdf_selected_shp:
            intersection = []
            area = area.to_crs(crs)
            area.set_crs(allow_override = True, crs = crs)

            # Soma da área de interseção feita com feição de input e atual área comparada
            # Essa soma é atribuida a uma nova coluna, identificada pelo nome da área comparada. Ex área quilombola: 108.4
            input.loc[0, self.result['operation_config']['shp'][index]['nome']] = gpd.overlay(input, area).area.sum()

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
                    self.load_layer(input.iloc[[0]], input_standard.iloc[[0]], area, intersection, index, None)
                else:
                    self.load_layer(input.iloc[[0]], input_standard, area, intersection, index, None)

            index += 1

    """
        Função compara a feição de input passada como parâmetro com bases de dados oriundas de bancos de dados.
        :parâmetro input: Feição ou shapefile de input, caso possua zona de proximidade inserida pelo usuário, a mesma será armazenado nesta variável.
        :parâmetro input_standard: Feição ou shapefile de input padrão isto é, sem zona de proximidade (caso necessário).
        :parâmetro gdf_selected_shp: Bases de dados de banco(s) de dado selecionados para comparação com a área de input.
        """
    def calculation_db(self, input, input_standard, gdf_selected_db):
        input = input.reset_index()
        intersection = []

        crs = 'EPSG:' + str(input.iloc[0]['crs_feature'])

        input = input.to_crs(crs)
        input.set_crs(crs, allow_override=True)

        if 'aproximacao' in self.result['operation_config']:
            input = self.utils.add_input_approximation_projected(input, self.result['operation_config']['aproximacao'])

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
                area.set_crs(allow_override = True, crs = crs)

                # Soma da área de interseção feita com feição de input e atual área comparada
                # Essa soma é atribuida a uma nova coluna, identificada pelo nome da área comparada. Ex área quilombola: 108.4
                input.loc[0, self.result['operation_config']['pg'][index_db]['nomeFantasiaTabelasCamadas'][
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

                intersection = gpd.GeoDataFrame(data, crs = input.crs)

                # Gera planta pdf somente quando acontece sobreposição
                if len(intersection) > 0:
                    intersection.set_crs(allow_override=True, crs=crs)

                    if len(input_standard) > 0:
                        self.load_layer(input.iloc[[0]], input_standard.iloc[[0]], area, intersection, index_db, index_layer)
                    else:
                        self.load_layer(input.iloc[[0]], input_standard, area, intersection, index_db, index_layer)

                index_layer += 1
            index_db += 1

    """
        Carrega camadas já processadas no QGis para que posteriormente possam ser gerados os relatórios no formato PDF.
        :parâmetro feature_input_gdp: Feição que está sendo processada e será carregada para o QGis.
        :parâmetro input_standard: Feição padrão isto é, sem zona de proximidade (caso necessário), que está sendo processada e será carregada para o QGis.
        :parâmetro feature_area: Camada de comparação que está sendo processada.
        :parâmetro feature_intersection: Camada de interseção (caso exista) e será carregada para o QGis.
        :parâmetro index_1: Variável utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar informções como estilização ou nome da camada.
        :parâmetro index_2: Variável utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar informções como estilização ou nome da camada.
    """
    def load_layer(self, feature_input_gdp, input_standard, feature_area, feature_intersection, index_1, index_2):
        # Remove camadas já impressas
        QgsProject.instance().removeAllMapLayers()
        QApplication.instance().processEvents()

        crs = (feature_input_gdp.iloc[0]['crs_feature'])
        # Forma de contornar problema do QGis, que alterava o extent da camada de forma incorreta
        extent = feature_input_gdp.bounds

        # Altera o EPSG do projeto QGis
        QgsProject.instance().setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))
        QApplication.instance().processEvents()
        # Carrega camada mundial do OpenStreetMap
        tms = 'type=xyz&url=http://a.tile.openstreetmap.org/{z}/{x}/{y}.png'
        layer = QgsRasterLayer(tms, 'OpenStreetMap', 'wms')
        QgsProject.instance().addMapLayer(layer)

        # Carrega camada de comparação no QGis
        # Se index 2 é diferente de None, significa que a comparação está vinda de banco de dados
        if index_2 == None:
            show_qgis_areas = QgsVectorLayer(feature_area.to_json(),
                                             self.result['operation_config']['shp'][index_1]['nomeFantasiaCamada'])
            show_qgis_areas.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

            symbol = self.get_feature_symbol(show_qgis_areas.geometryType(), self.result['operation_config']['shp'][index_1]['estiloCamadas'][0])
            show_qgis_areas.renderer().setSymbol(symbol)
            QgsProject.instance().addMapLayer(show_qgis_areas)
        else:
            if 'geom' in feature_area:
                feature_area = feature_area.drop(columns=['geom'])

            feature_area = feature_area.drop_duplicates()

            show_qgis_areas = QgsVectorLayer(feature_area.to_json(),
                                             self.result['operation_config']['pg'][index_1]['nomeFantasiaTabelasCamadas'][index_2])
            show_qgis_areas.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

            symbol = self.get_feature_symbol(show_qgis_areas.geometryType(), self.result['operation_config']['pg'][index_1]['estiloTabelasCamadas'][index_2])
            show_qgis_areas.renderer().setSymbol(symbol)
            QgsProject.instance().addMapLayer(show_qgis_areas)

        # Carrega a área padrão no QGis, sem área de aproximação (caso necessário)
        if 'aproximacao' in self.result['operation_config']:
            # Carrega camada de input no QGis (Caso usuário tenha inserido como entrada, a área de aproximação está nesta camada)
            show_qgis_input = QgsVectorLayer(feature_input_gdp.to_json(), "Feição de Estudo/Sobreposição")
            show_qgis_input.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

            symbol = self.get_input_symbol(show_qgis_input.geometryType())
            show_qgis_input.renderer().setSymbol(symbol)
            QgsProject.instance().addMapLayer(show_qgis_input)

            if index_2 != None:
                input_standard = input_standard.to_crs(crs)
            show_qgis_input_standard = QgsVectorLayer(input_standard.to_json(), "Feição de Estudo/Sobreposição (padrão)")
            show_qgis_input_standard.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

            symbol = self.get_input_standard_symbol(show_qgis_input_standard.geometryType())
            show_qgis_input_standard.renderer().setSymbol(symbol)
            QgsProject.instance().addMapLayer(show_qgis_input_standard)
        else:
            # Carrega camada de input no QGis (Caso usuário tenha inserido como entrada, a área de aproximação está nesta camada)
            show_qgis_input = QgsVectorLayer(feature_input_gdp.to_json(), "Feição de Estudo/Sobreposição")
            show_qgis_input.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

            symbol = self.get_input_standard_symbol(show_qgis_input.geometryType())
            show_qgis_input.renderer().setSymbol(symbol)
            QgsProject.instance().addMapLayer(show_qgis_input)

        # Carrega as áreas de intersecção no Qgis
        if len(feature_intersection) > 0:
            show_qgis_intersection = QgsVectorLayer(feature_intersection.to_json(), "Sobreposição")
            show_qgis_intersection.setCrs(QgsCoordinateReferenceSystem('EPSG:' + str(crs)))

            symbol = QgsFillSymbol.createSimple(
                {'line_style': 'solid', 'line_color': 'black', 'color': 'yellow', 'width_border': '0,35',
                 'style': 'solid'})
            show_qgis_intersection.renderer().setSymbol(symbol)
            QgsProject.instance().addMapLayer(show_qgis_intersection)

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

    """
        Função responsável carregar o layout de impressão e por gerar os arquivos PDF.
        :parâmetro feature_input_gdp: Feição de input comparada 
        :parâmetro index_1: Variável utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar informções como estilização ou nome da camada.
        :parâmetro index_2: Variável utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar informções como estilização ou nome da camada.
    """
    def export_pdf(self, feature_input_gdp, index_1, index_2):
        # Manipulação dos textos do layout
        self.handle_text(index_1, index_2)

        if 'logradouro' not in feature_input_gdp:
            feature_input_gdp['logradouro'] = "Ponto por Endereço ou Coordenada"

        if index_2 == None:
            pdf_name = str(feature_input_gdp.iloc[0]['logradouro']) + '_' + str(self.result['operation_config']['shp'][index_1]['nomeFantasiaCamada']) + '.pdf'
        else:
            pdf_name = str(feature_input_gdp.iloc[0]['logradouro']) + '_' + str(self.result['operation_config']['pg'][index_1]['nomeFantasiaTabelasCamadas'][index_2]) + '.pdf'

        pdf_path = os.path.join(self.result['path_output'], pdf_name)

        print(pdf_path)

        atlas = self.layout.atlas()
        map_atlas = atlas.layout()
        pdf_settings = QgsLayoutExporter(map_atlas).PdfExportSettings()
        pdf_settings.dpi = 150

        if atlas.enabled():
            pdf_settings.rasterizeWholeImage = True
            QgsLayoutExporter.exportToPdf(atlas, pdf_path,
                                           settings=pdf_settings)

    QApplication.instance().processEvents()

    """
        Faz a manipulação de alguns dados textuais presentes no layout de impressão.
        :parâmetro index_1: Variável utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar informções como estilização ou nome da camada.
        :parâmetro index_2: Variável utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar informções como estilização ou nome da camada.
    """
    def handle_text(self, index_1, index_2):

        et = EnvTools()
        headers = et.get_report_hearder()

        spu = self.layout.itemById('CD_UnidadeSPU')
        spu.setText(headers['superintendencia'])

        sector = self.layout.itemById('CD_SubUnidadeSPU')
        sector.setText(headers['setor'])

        title = self.layout.itemById('CD_Titulo')
        if index_2 == None:
            title.setText('Caracterização: ' + self.result['operation_config']['shp'][index_1]['nomeFantasiaCamada'])
        else:
            title.setText('Caracterização: ' + self.result['operation_config']['pg'][index_1]['nomeFantasiaTabelasCamadas'][index_2])

    """
        Adiciona o template do layout ao projeto atual.
        :parâmetro template_dir: Variável armazena o local do layout.
    """
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

    """
        Estilização dinâmica para diferentes tipos de geometrias (Área de input).
        :parâmetro geometry_type: Tipo de geometria da área de input (com ou se buffer de área de aproximação).
    """
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

    """
        Estilização dinâmica para diferentes tipos de geometrias (Área de input sem o buffer de aproximação).
        :parâmetro geometry_type: Tipo de geometria da área de input sem o buffer de aproximação.
    """
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
            symbol = QgsFillSymbol.createSimple(
                {'line_style': 'solid', 'line_color': 'black', 'color': 'gray', 'width_border': '0,35',
                 'style': 'solid'})

        return symbol

    """
        Estilização dinâmica para diferentes tipos de geometrias (Áreas de comparação).
        :parâmetro geometry_type: Tipo de geometria da área de comparação.
    """
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