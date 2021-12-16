import os

from qgis import processing

from qgis.PyQt.QtWidgets import QApplication
from qgis.core import *
from qgis.PyQt.QtXml import QDomDocument
from qgis.utils import iface

import geopandas as gpd

class LayoutManager():
    def __init__(self, result, progress_bar):
        super().__init__()
        self.result = result
        self.progress_bar = progress_bar
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
        input_standard = self.result['input_standard']
        gdf_selected_shp = self.result['gdf_selected_shp']
        gdf_selected_db = self.result['gdf_selected_db']
        # Verifica fuso das features do input
        input = self.get_utm_crs(input)

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
                    self.calculation_shp(input.loc[[indexInput]], input_standard.loc[[indexInput]],  gdf_selected_shp)
                    self.calculation_db(input.loc[[indexInput]], input_standard.loc[[indexInput]], gdf_selected_db)
                else:
                    self.calculation_shp(input.loc[[indexInput]], input_standard, gdf_selected_shp)
                    self.calculation_db(input.loc[[indexInput]], input_standard, gdf_selected_db)
            atual_progress += interval_progress
            self.progress_bar.setValue(atual_progress)

    def calculation_shp(self, input, input_standard, gdf_selected_shp):
        input = input.reset_index()

        # Transforma a feição de input o crs em que está inserido dentro das Zonas UTM
        crs = 'EPSG:' + str(input.loc[0]['crs_feature'])
        input = input.to_crs(crs)

        # Cálculos de área e centroid da feição de input
        input.loc[0, 'areaLote'] = input.loc[0]['geometry'].area
        input.loc[0, 'ctr_lat'] = input.loc[0]['geometry'].centroid.y
        input.loc[0, 'ctr_long'] = input.loc[0]['geometry'].centroid.x

        index = 0
        # Compara a feição de entrada com todas as áreas de comparação shp selecionadas pelo usuário
        for area in gdf_selected_shp:
            intersection = []
            area = area.to_crs(crs)

            # Soma da área de interseção feita com feição de input e atual área comparada
            # Essa soma é atribuida a uma nova coluna, identificada pelo nome da área comparada. Ex área quilombola: 108.4
            input.loc[0, self.result['operation_config']['shp'][index]['nome']] = gpd.overlay(input, area).area.sum()

            data = []
            # Armazena em um novo GeoDataFrame (intersection) as áreas de interseção entre feição de entrada e feição
            # da atual área que está sendo comparada. Realiza ainda cálculo de área e centroid para a nova geomatria de interseção
            for indexArea, rowArea in area.iterrows():
                if (input.loc[0]['geometry'].intersection(rowArea['geometry'])):
                    data.append({
                        'areaLote': input.loc[0]['geometry'].intersection(rowArea['geometry']).area,
                        'ctr_lat': input.loc[0]['geometry'].intersection(rowArea['geometry']).centroid.y,
                        'ctr_long': input.loc[0]['geometry'].intersection(rowArea['geometry']).centroid.x,
                        'geometry': input.loc[0]['geometry'].intersection(rowArea['geometry'])
                    })

            intersection = gpd.GeoDataFrame(data, crs=input.crs)

            if len(input_standard) > 0:
                self.load_layer(input.iloc[[0]], input_standard.iloc[[0]], area, intersection, index, None)
            else:
                self.load_layer(input.iloc[[0]], input_standard, area, intersection, index, None)


            index += 1

    def calculation_db(self, input, input_standard, gdf_selected_db):
        input = input.reset_index()
        intersection = []

        crs = 'EPSG:' + str(input.loc[0]['crs_feature'])
        input = input.to_crs(crs)

        # Cálculos de área de input e centroid feição de entrada
        input.loc[0, 'areaLote'] = input.loc[0]['geometry'].area
        input.loc[0, 'ctr_lat'] = input.loc[0]['geometry'].centroid.y
        input.loc[0, 'ctr_long'] = input.loc[0]['geometry'].centroid.x

        index_db = 0
        # Compara a feição de entrada com todas as áreas de comparação db selecionadas pelo usuário
        for db in gdf_selected_db:
            index_layer = 0
            for area in db:
                area.crs = 'EPSG:4674'
                area = area.to_crs(crs)

                # Soma da área de interseção feita com feição de input e atual área comparada
                # Essa soma é atribuida a uma nova coluna, identificada pelo nome da área comparada. Ex área quilombola: 108.4
                input.loc[0, self.result['operation_config']['pg'][index_db]['nomeFantasiaTabelasCamadas'][
                    index_layer]] = gpd.overlay(input, area).area.sum()

                data = []
                # Armazena em um novo GeoDataFrame (intersection) as áreas de interseção entre feição de entrada e feição
                # da atual área que está sendo comparada. Realiza ainda cálculo de área e centroid para a nova geomatria de interseção
                for indexArea, rowArea in area.iterrows():
                    if (input.loc[0]['geometry'].intersection(rowArea['geometry'])):
                        data.append({
                            'areaLote': input.loc[0]['geometry'].intersection(rowArea['geometry']).area,
                            'ctr_lat': input.loc[0]['geometry'].intersection(rowArea['geometry']).centroid.y,
                            'ctr_long': input.loc[0]['geometry'].intersection(rowArea['geometry']).centroid.x,
                            'geometry': input.loc[0]['geometry'].intersection(rowArea['geometry'])
                        })

                intersection = gpd.GeoDataFrame(data, crs = input.crs)

                if len(input_standard) > 0:
                    self.load_layer(input.iloc[[0]], input_standard.iloc[[0]], area, intersection, index_db, index_layer)
                else:
                    self.load_layer(input.iloc[[0]], input_standard, area, intersection, index_db, index_layer)

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

    # Carrega camadas já processadas no QGis para que posteriormente possam ser gerados os relatórios no formato PDF
    def load_layer(self, feature_input_gdp, input_standard, feature_area, feature_intersection, index_1, index_2):
        crs = (feature_input_gdp.iloc[0]['crs_feature'])
        # Forma de contornar problema do QGis, que alterava o extent da camada de forma incorreta
        get_extent = feature_input_gdp.to_crs(crs)
        extent = feature_input_gdp.bounds

        # Transforma todas camadas para EPSG geográfico, deixando a reprojeção para o QGis
        feature_input_gdp = feature_input_gdp.to_crs(4674)
        feature_area = feature_area.to_crs(4674)
        if len(feature_intersection) > 0:
            print(feature_intersection)
            feature_intersection = feature_intersection.to_crs(4674)

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

        # Carrega camada de input no QGis (Caso usuário tenha inserido como entrada, a área de aproximação está nesta camada)
        show_qgis_input = QgsVectorLayer(feature_input_gdp.to_json(), "Lote (padrão)")

        symbol = QgsFillSymbol.createSimple(
            {'line_style': 'solid', 'line_color': 'black', 'color': '#616161', 'width_border': '0,35',
             'style': 'solid'})
        show_qgis_input.renderer().setSymbol(symbol)
        QgsProject.instance().addMapLayer(show_qgis_input)

        # Carrega a área padrão no QGis, sem área de aproximação (caso necessário)
        if len(input_standard) > 0:
            show_qgis_input_standard = QgsVectorLayer(input_standard.to_json(), "Lote (faixa de proximidade)")

            symbol = QgsFillSymbol.createSimple(
                {'line_style': 'solid', 'line_color': 'black', 'color': 'gray', 'width_border': '0,35',
                 'style': 'solid'})
            show_qgis_input_standard.renderer().setSymbol(symbol)
            QgsProject.instance().addMapLayer(show_qgis_input_standard)

        # Carrega as áreas de intersecção no Qgis
        if len(feature_intersection) > 0:
            show_qgis_intersection = QgsVectorLayer(feature_intersection.to_json(), "Sobreposição")

            symbol = QgsFillSymbol.createSimple(
                {'line_style': 'solid', 'line_color': 'black', 'color': 'yellow', 'width_border': '0,35',
                 'style': 'solid'})
            show_qgis_intersection.renderer().setSymbol(symbol)
            QgsProject.instance().addMapLayer(show_qgis_intersection)

        # Posiciona a tela do QGis no extent da área de entrada
        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() == 'Lote (padrão)':
                rect = QgsRectangle(extent['minx'], extent['miny'], extent['maxx'], extent['maxy'])
                # Aqui está sendo contornado o erro de transformação, comentado no comeco desta função
                layer.setExtent(rect)
                self.layers = layer

        iface.mapCanvas().refresh()

        # Configurações no QGis para gerar os relatórios PDF
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

        main_map.refresh()

        # Tamanho do mapa no layout
        main_map.attemptResize(QgsLayoutSize(390, 277, QgsUnitTypes.LayoutMillimeters))

        self.pdf_generator(feature_input_gdp, feature_area, index_1, index_2)

        # Remove camadas já impressas
        QgsProject.instance().removeAllMapLayers()
        QApplication.instance().processEvents()

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
