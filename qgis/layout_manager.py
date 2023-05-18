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
from ..environment import NOME_CAMADA_INTERSECAO_POLIGONO, NOME_CAMADA_INTERSECAO_LINHA

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

            self.handle_required_layers(self.dic_layers_ever)

            self.export_relatorio_sintese()
            self.export_relatorio_mapa()
            # self.export_relatorio_vertices()
            self.remover_camadas_intersecoes()
            self.merge_pdf()
        
    def handle_required_layers(self, data):
        lyr_overlay_point = data['lyr_overlap_point'] if 'lyr_overlap_point' in data else None
        lyr_overlay_line = data['lyr_overlap_line'] if 'lyr_overlap_line' in data else None
        lyr_overlay_polygon = data['lyr_overlap_polygon'] if 'lyr_overlap_polygon' in data else None
        
        overlay_layer = QgsVectorLayer("Polygon?crs=EPSG:4326", "Nova Camada", "memory")
        provider = overlay_layer.dataProvider()

        if self.feature.geometry().wkbType() in [QgsWkbTypes.Polygon, QgsWkbTypes.MultiPolygon]:
            if lyr_overlay_polygon:
                for feature_overlay in lyr_overlay_polygon.getFeatures():
                    if feature_overlay.attribute('Camada_sobreposicao') == 'Área Homologada' and feature_overlay.attribute('logradouro') == self.feature.attribute('logradouro'):
                        nova_feature = QgsFeature()
                        nova_feature.setGeometry(feature_overlay.geometry())
                        provider.addFeatures([nova_feature])
                overlay_layer.setName(NOME_CAMADA_INTERSECAO_POLIGONO)

        elif self.feature.geometry().wkbType() in [QgsWkbTypes.Point, QgsWkbTypes.MultiPoint]:
            pass

        elif self.feature.geometry().wkbType() in [QgsWkbTypes.LineString, QgsWkbTypes.MultiLineString]:
            if lyr_overlay_polygon:
                for feature_overlay in lyr_overlay_polygon.getFeatures():
                    if feature_overlay.attribute('logradouro') == self.feature.attribute('logradouro'):
                        nova_feature = QgsFeature()
                        nova_feature.setGeometry(feature_overlay.geometry())
                        provider.addFeatures([nova_feature])
                overlay_layer.setName(NOME_CAMADA_INTERSECAO_LINHA)
        
        QgsProject.instance().addMapLayer(overlay_layer)
        

    def remover_camadas_intersecoes(self):
        camadas = QgsProject.instance().mapLayers().values()
        nomes_camadas_remover = ["Interseções (Polígono)", "Interseções (Linha)", "Interseções (Ponto)"]

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

    def export_relatorio_mapa(self):
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
        item_layout.setText('Lote não sobrepõe Área Homologada')
        overlay_uniao_area = layout.itemById('CD_Compl_Obs4')
        overlay_uniao_area.setText("Área de sobreposição com Área Homologada: 0,00 m².")
        if feature_encontrada:
            column_value = feature_encontrada.attribute(column_index)
            
            if "Área Homologada" in column_value:
                item_layout.setText('Lote sobrepõe Área Homologada')
                item_layout = layout.itemById('CD_Titulo')
                item_layout.setText(f'Caracterização: Áreas da União')

                get_overlay_area = QgsProject.instance().mapLayersByName(NOME_CAMADA_INTERSECAO_POLIGONO)[0] or QgsProject.instance().mapLayersByName(NOME_CAMADA_INTERSECAO_LINHA)[0]
                if get_overlay_area:
                    overlay_uniao_area.setText("Área de sobreposição com Área Homologada: " + str(self.overlay_analisys.calcular_soma_areas(get_overlay_area, self.feature.attribute('EPSG_S2000'))) + " m².")


        lyr_utils.export_atlas_single_page(self.lyr_input, self.feature, layout_name, self.pdf_name, self.path_output, f'{self.time}_B_Mapa')

    def export_relatorio_vertices(self):
        layout_name = 'relatorio'

        layout = QgsProject.instance().layoutManager().layoutByName(layout_name)

        lyr_utils.export_atlas_single_page(self.lyr_input, self.feature, layout_name, self.pdf_name, self.path_output, 'Vértices')

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
        