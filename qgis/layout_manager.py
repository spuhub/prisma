# -*- coding: utf-8 -*-
import os

from qgis.core import (
    QgsProject,
    QgsVectorFileWriter,
    QgsVectorLayer, 
    QgsField, 
    QgsFeature, 
    QgsPrintLayout,
    QgsReadWriteContext,
    QgsCoordinateReferenceSystem,
    QgsRasterLayer,
    QgsWkbTypes,
    QgsGeometry
    )
from PyPDF2 import PdfReader, PdfMerger
from datetime import datetime
from qgis.PyQt.QtWidgets import QApplication
from qgis.PyQt.QtXml import QDomDocument
from PyQt5 import QtCore
from qgis.utils import iface
from qgis.PyQt.QtCore import QVariant

from ..utils import lyr_utils
from ..utils.utils import Utils
from ..analysis.overlay_analysis import OverlayAnalisys
from ..settings.env_tools import EnvTools
from ..environment import NOME_CAMADA_INTERSECAO_POLIGONO, NOME_CAMADA_INTERSECAO_LINHA, NOME_CAMADA_INTERSECAO_PONTO

class LayoutManager():
    """Classe responsável por fazer a manipulação do Layout de impressão. 
    Contém métodos para fazer o controle das feições carregadas para impressão,
    manipular textos e também algumas operações com dados que serão plotados ou 
    utilizados para gerar relatórios PDF.

    """

    def __init__(self, data, progress_bar):

        date_and_time = datetime.now()
        self.time = date_and_time.strftime('%Y-%m-%d_%H-%M-%S')
        self.pdf_name: str = ''
        self.overlay_analisys = OverlayAnalisys()

        self.feature: QgsFeature
        self.dic_layers = data['layers']
        self.dic_layers_ever = data['layers'].copy()
        self.overlaps = data['overlaps']
        self.possui_buffer = True if (('aproximacao' in data['operation_config']['input']) and data['operation_config']['input']['aproximacao'] > 0) else False
        self.lyr_input = self.dic_layers['input_buffer'] if self.possui_buffer else self.dic_layers['input']
        self.operation_config = data['operation_config']
        self.path_output = data['path_output']
        self.progress_bar = progress_bar

        self.utils = Utils()
        self.basemap_name, self.basemap_link = self.utils.get_active_basemap()
        
        template_dir = os.path.join(os.path.dirname(__file__), r'layouts\Planta_FolhaA3_Paisagem.qpt')
        self.add_template_to_project(template_dir)

        template_dir = os.path.join(os.path.dirname(__file__), r'layouts\Relatorio_FolhaA4_Retrato.qpt')
        self.add_template_to_project(template_dir)

        template_dir = os.path.join(os.path.dirname(__file__), r'layouts\Folha_VerticesA4_Retrato.qpt')
        self.add_template_to_project(template_dir)

        lyr_com_sobrep, lyr_sem_sobrep = self.identifica_info_sobrep()

        basemap_layer: QgsVectorLayer
        if 'basemap' in data['operation_config']:
            basemap_layer = QgsRasterLayer(self.basemap_link, self.basemap_name, 'wms')
        else:
            # Carrega camada mundial do OpenStreetMap
            tms = 'type=xyz&url=http://a.tile.openstreetmap.org/{z}/{x}/{y}.png'
            basemap_layer = QgsRasterLayer(tms, 'OpenStreetMap', 'wms')

        QgsProject.instance().addMapLayer(lyr_com_sobrep.clone())
        QgsProject.instance().addMapLayer(lyr_sem_sobrep.clone())
        QgsProject.instance().addMapLayer(basemap_layer.clone())
        QgsProject.instance().addMapLayer(self.lyr_input.clone())
        # lyr_overlay_polygon = data['layers']['lyr_overlap_polygon']
        # QgsProject.instance().addMapLayer(lyr_overlay_polygon.clone())

        for layer in self.dic_layers['required']:
            QgsProject.instance().addMapLayer(layer.clone())

        # Repaint the canvas map
        iface.mapCanvas().refresh()

        for feature in self.lyr_input.getFeatures():
            self.feature = feature
            self.pdf_name = f'{feature["logradouro"]}_{self.time}'

            self.handle_layers(self.dic_layers_ever, "Área Homologada")
            self.export_relatorio_sintese()
            self.export_relatorio_mapa("Área Homologada")
            # self.export_relatorio_vertices()
            self.remover_camadas_intersecoes()
            self.merge_pdf()

        self.remover_camadas_obrigatorias()

        for feature in self.lyr_input.getFeatures():
            self.feature = feature
            self.pdf_name = f'{feature["logradouro"]}_{self.time}'
            for layer_comp in self.dic_layers_ever['shp']:
                if feature.attribute(layer_comp.name()) == True: # TODO: REMOVER ISSO
                    print_lyr = layer_comp.clone()
                    QgsProject.instance().addMapLayer(print_lyr)
                    self.handle_layers(self.dic_layers_ever, layer_comp.name())
                    self.export_relatorio_mapa(layer_comp.name())
                    # self.export_relatorio_vertices()
                    QgsProject.instance().removeMapLayer(print_lyr.id())
                    self.remover_camadas_intersecoes()
                    self.merge_pdf()
        
    def handle_layers(self, data, lyr_comp_name):
        lyr_overlay_point = data['lyr_overlap_point'] if 'lyr_overlap_point' in data else None
        lyr_overlay_line = data['lyr_overlap_line'] if 'lyr_overlap_line' in data else None
        lyr_overlay_polygon = data['lyr_overlap_polygon'] if 'lyr_overlap_polygon' in data else None

        if self.feature.geometry().wkbType() in [QgsWkbTypes.Polygon, QgsWkbTypes.MultiPolygon]:
            overlay_layer = QgsVectorLayer("Polygon?crs=EPSG:4326", NOME_CAMADA_INTERSECAO_POLIGONO, "memory")
            provider = overlay_layer.dataProvider()
            if lyr_overlay_polygon:
                for feature_overlay in lyr_overlay_polygon.getFeatures():
                    if feature_overlay.attribute('Camada_sobreposicao') == lyr_comp_name and feature_overlay.attribute('logradouro') == self.feature.attribute('logradouro'):
                        nova_feature = QgsFeature()
                        nova_feature.setGeometry(feature_overlay.geometry())
                        provider.addFeatures([nova_feature])
                QgsProject.instance().addMapLayer(overlay_layer)

        elif self.feature.geometry().wkbType() in [QgsWkbTypes.Point, QgsWkbTypes.MultiPoint]:
            if lyr_overlay_point:
                for feature_overlay in lyr_overlay_point.getFeatures():
                    if feature_overlay.attribute('logradouro') == self.feature.attribute('logradouro'):
                        nova_feature = QgsFeature()
                        nova_feature.setGeometry(feature_overlay.geometry())
                        provider.addFeatures([nova_feature])
                overlay_layer.setName(NOME_CAMADA_INTERSECAO_PONTO)

        elif self.feature.geometry().wkbType() in [QgsWkbTypes.LineString, QgsWkbTypes.MultiLineString]:
            overlay_layer = QgsVectorLayer("LineString?crs=EPSG:4326", NOME_CAMADA_INTERSECAO_LINHA, "memory")
            provider = overlay_layer.dataProvider()
            if lyr_overlay_line:
                for feature_overlay in lyr_overlay_line.getFeatures():
                    if feature_overlay.attribute('Camada_sobreposicao') == lyr_comp_name and feature_overlay.attribute('logradouro') == self.feature.attribute('logradouro'):
                        nova_feature = QgsFeature()
                        nova_feature.setGeometry(feature_overlay.geometry())
                        provider.addFeatures([nova_feature])
                QgsProject.instance().addMapLayer(overlay_layer)
        
        
        

    def remover_camadas_intersecoes(self):
        camadas = QgsProject.instance().mapLayers().values()
        nomes_camadas_remover = ["Interseções (Polígono)", "Interseções (Linha)", "Interseções (Ponto)"]

        for camada in camadas:
            if camada.name() in nomes_camadas_remover:
                QgsProject.instance().removeMapLayer(camada)

    def remover_camadas_obrigatorias(self):
        camadas = QgsProject.instance().mapLayers().values()
        nomes_camadas_remover = ["Área Homologada", "Área não Homologada", "LTM Homologada", "LTM não Homologada", "LPM Homologada", "LPM não Homologada"]

        for camada in camadas:
            if camada.name() in nomes_camadas_remover:
                QgsProject.instance().removeMapLayer(camada)

    def identifica_info_sobrep(self):
        dic_lyr_com_sobrep = {}
        dic_lyr_sem_sobrep = {}
        list_feats_com_sobrep = []
        list_feats_sem_sobrep = []
        lyr_com_sobrep = QgsVectorLayer('None', 'Com_Sobreposicao', 'memory')
        lyr_sem_sobrep = QgsVectorLayer('None', 'Sem_Sobreposicao', 'memory')

        lyr_com_sobrep.dataProvider().addAttributes([QgsField('feat_id', QtCore.QVariant.Int),
                                                     QgsField('list_layer', QtCore.QVariant.String)])
        lyr_sem_sobrep.dataProvider().addAttributes([QgsField('feat_id', QtCore.QVariant.Int),
                                                     QgsField('list_layer', QtCore.QVariant.String)])
        
        lyr_com_sobrep.updateFields()
        lyr_sem_sobrep.updateFields()

        # Adiciona um novo campo "id_feature" na camada
        self.lyr_input.startEditing()
        new_field = QgsField("id", QVariant.Int)
        self.lyr_input.dataProvider().addAttributes([new_field])
        self.lyr_input.updateFields()

        for layer_item in self.dic_layers:
            if layer_item not in ('input', 'input_buffer', 'lyr_vertices', 'lyr_overlap_point', 'lyr_overlap_line', 'lyr_overlap_polygon'):
                list_type = self.dic_layers[layer_item]
                for idx, layer in enumerate(list_type):
                    for feature in self.lyr_input.getFeatures():
                        index = self.lyr_input.fields().indexFromName('id')
                        self.lyr_input.changeAttributeValue(feature.id(), index, feature.id())
                        value = feature[layer.name()]
                        if value:
                            if feature.id() not in dic_lyr_com_sobrep:
                                dic_lyr_com_sobrep[feature.id()] = [layer.name()]
                            else:
                                dic_lyr_com_sobrep[feature.id()].append(layer.name())
                        else:
                            if feature.id() not in dic_lyr_sem_sobrep:
                                dic_lyr_sem_sobrep[feature.id()] = [layer.name()]
                            else:
                                dic_lyr_sem_sobrep[feature.id()].append(layer.name())
        
        self.lyr_input.commitChanges()
        
        for item in dic_lyr_com_sobrep:
            feat = QgsFeature(lyr_com_sobrep.fields())

            feat_id = item
            list_layer = ', '.join(dic_lyr_com_sobrep[item])
            feat.setAttributes([feat_id, list_layer])
            list_feats_com_sobrep.append(feat)
        
        for item in dic_lyr_sem_sobrep:
            feat = QgsFeature(lyr_sem_sobrep.fields())

            feat_id = item
            list_layer = ', '.join(dic_lyr_sem_sobrep[item])
            feat.setAttributes([feat_id, list_layer])
            list_feats_sem_sobrep.append(feat)

        lyr_com_sobrep.dataProvider().addFeatures(list_feats_com_sobrep)
        lyr_sem_sobrep.dataProvider().addFeatures(list_feats_sem_sobrep)

        return lyr_com_sobrep, lyr_sem_sobrep

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

    def export_relatorio_sintese(self):
        layout_name = 'Relatorio_FolhaA4_Retrato'
        layout = QgsProject.instance().layoutManager().layoutByName(layout_name)
            
        lyr_utils.export_atlas_single_page(self.lyr_input, self.feature, layout_name, self.pdf_name, self.path_output, f'{self.time}_A_Relatorio')

    def export_relatorio_mapa(self, layer_name):
        layout_name = 'Planta_FolhaA3_Paisagem'
        layout = QgsProject.instance().layoutManager().layoutByName(layout_name)

        lyr_com_sobrep = QgsProject.instance().mapLayersByName('Com_Sobreposicao')[0]   
        column_index = lyr_com_sobrep.fields().indexFromName('list_layer')
        
        get_overlay_area = None
        feature_encontrada = None
        for feature in lyr_com_sobrep.getFeatures():
            if feature['feat_id'] == self.feature.id():
                feature_encontrada = feature
                break

        item_layout = layout.itemById('CD_Compl_Obs1')
        item_layout.setText(f'Lote não sobrepõe {layer_name}')
        overlay_uniao_area = layout.itemById('CD_Compl_Obs3')
        overlay_uniao_area.setText(f"Área de sobreposição com {layer_name}: 0,00 m².")
        if feature_encontrada:
            column_value = feature_encontrada.attribute(column_index)
            
            if layer_name in column_value:
                item_layout.setText(f'Lote sobrepõe {layer_name}')
                item_layout = layout.itemById('CD_Titulo')
                item_layout.setText(f'Caracterização: {layer_name}')

                get_overlay_area = QgsProject.instance().mapLayersByName(NOME_CAMADA_INTERSECAO_POLIGONO) or QgsProject.instance().mapLayersByName(NOME_CAMADA_INTERSECAO_LINHA)
                if get_overlay_area:
                    if isinstance(get_overlay_area, list):
                        get_overlay_area = get_overlay_area[0]
                    overlay_uniao_area.setText(f"Área de sobreposição com {layer_name}: " + str(self.overlay_analisys.calcular_soma_areas(get_overlay_area, self.feature.attribute('EPSG_S2000'))) + " m².")

        self.handle_text(layout)
        lyr_utils.export_atlas_single_page(self.lyr_input, self.feature, layout_name, self.pdf_name, self.path_output, f'{self.time}_B_Mapa')

    def export_relatorio_vertices(self):
        layout_name = 'relatorio'

        layout = QgsProject.instance().layoutManager().layoutByName(layout_name)

        lyr_utils.export_atlas_single_page(self.lyr_input, self.feature, layout_name, self.pdf_name, self.path_output, '_C_Vértices')

    def merge_pdf(self):
        pdf_name = "_".join(self.pdf_name.split("_", 3)[:3])

        pdf_files = [f for f in os.listdir(self.path_output) if f.startswith(pdf_name) and f.endswith(".pdf")]
        merger = PdfMerger()

        for filename in pdf_files:
            merger.append(PdfReader(os.path.join(self.path_output, filename), "rb"))

        merger.write(os.path.join(self.path_output, pdf_name + ".pdf"))

        for filename in os.listdir(self.path_output):
            if pdf_name in filename and filename.count("_") > 2:
                os.remove(self.path_output + "/" + filename)

    def handle_text(self, layout):
        """
        Faz a manipulação de alguns dados textuais presentes no layout de impressão.

        @keyword index_1: Variável utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar informções como estilização ou nome da camada.
        @keyword index_2: Variável utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar informções como estilização ou nome da camada.
        """
        et = EnvTools()
        headers = et.get_report_hearder()

        spu = layout.itemById('CD_UnidadeSPU')
        spu.setText(headers['superintendencia'])

        sector = layout.itemById('CD_SubUnidadeSPU')
        sector.setText(headers['setor'])