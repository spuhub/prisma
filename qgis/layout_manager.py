# -*- coding: utf-8 -*-
import os
import sys
import math

from qgis.core import (
    QgsProject,
    QgsVectorLayer, 
    QgsField, 
    QgsFeature, 
    QgsPrintLayout,
    QgsReadWriteContext,
    QgsRasterLayer,
    QgsWkbTypes,
    QgsCoordinateReferenceSystem
    )

from PyPDF2 import PdfReader, PdfMerger
from datetime import datetime
from qgis.PyQt.QtXml import QDomDocument
from PyQt5 import QtCore
from qgis.utils import iface
from qgis.PyQt.QtCore import QVariant
from PyQt5.QtWidgets import QApplication

from ..utils import lyr_utils
from ..utils.utils import Utils
from ..analysis.overlay_analysis import OverlayAnalisys
from ..settings.env_tools import EnvTools

from ..environment import (
    NOME_CAMADA_INTERSECAO_PONTO,
    NOME_CAMADA_INTERSECAO_LINHA,
    NOME_CAMADA_INTERSECAO_POLIGONO,
    CAMADA_DE_PONTO,
    CAMADA_DE_LINHA,
    CAMADA_DE_POLIGONO,
    NOME_CAMADA_VERTICES,
    NOME_CAMADA_QUOTAS,
    CRS_PADRAO
    
)

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
        self.lyr_comp_geometry: QgsWkbTypes
        self.dic_layers = data['layers']
        self.dic_layers_ever = data['layers'].copy()
        self.overlaps = data['overlaps']
        self.possui_buffer = True if (('aproximacao' in data['operation_config']['input']) and data['operation_config']['input']['aproximacao'] > 0) else False
        self.lyr_input = self.dic_layers['input_buffer'] if self.possui_buffer else self.dic_layers['input']
        self.operation_config = data['operation_config']
        self.path_output = data['path_output']
        self.project_layers = []
        self.utils = Utils()
        self.current_year: str = str(datetime.now().year)
        self.basemap_name, self.basemap_link = self.utils.get_active_basemap()

        self.progress_bar = progress_bar
        self.progress_bar.setHidden(False)
        self.progress_bar.setRange(0, 100)        
        self.actual_progress = 0
        self.progress_bar.setValue(self.actual_progress)
        self.total_comp = len(self.dic_layers_ever['shp']) + len(self.dic_layers_ever['db']) + len(self.dic_layers_ever['wfs'])
        
        for lyr in self.dic_layers_ever['required']: 
            if lyr.name() == "Área Homologada":
                self.total_comp = self.total_comp + 1
            
        self.total_comp = self.total_comp * self.lyr_input.featureCount()

        is_windows = sys.platform.startswith('win')
        
        template_dir = os.path.join(os.path.dirname(__file__), r'layouts\Planta_FolhaA3_Paisagem.qpt' if is_windows else r'layouts/Planta_FolhaA3_Paisagem.qpt')
        self.add_template_to_project(template_dir)

        template_dir = os.path.join(os.path.dirname(__file__), r'layouts\Relatorio_FolhaA4_Retrato.qpt' if is_windows else r'layouts/Relatorio_FolhaA4_Retrato.qpt')
        self.add_template_to_project(template_dir)

        template_dir = os.path.join(os.path.dirname(__file__), r'layouts\Folha_VerticesA4_Retrato.qpt' if is_windows else r'layouts/Folha_VerticesA4_Retrato.qpt')
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
            self.lyr_comp_geometry = "Polygon"
            self.pdf_name = f'{feature["logradouro"]}_{self.time}'

            self.handle_layers(self.dic_layers_ever, "Área Homologada")
            self.adiciona_camada_vertices()
            self.export_relatorio_sintese()
            self.export_relatorio_mapa("Área Homologada")
            # self.export_relatorio_vertices()
            self.remover_camadas("Interseções")
            self.remover_camadas("Vértices")
            self.merge_pdf()
            self.update_progress_bar()

        self.remover_camadas_obrigatorias()

        for feature in self.lyr_input.getFeatures():
            self.feature = feature
            self.pdf_name = f'{feature["logradouro"]}_{self.time}'
            for layer_comp in self.dic_layers_ever['shp']:
                self.lyr_comp_geometry = lyr_utils.get_general_geom_type_name(layer_comp)
                if feature.attribute(layer_comp.name()) == True:
                    print_lyr = layer_comp.clone()
                    QgsProject.instance().addMapLayer(print_lyr)
                    self.handle_layers(self.dic_layers_ever, layer_comp.name())
                    self.adiciona_camada_vertices()
                    self.project_layers = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
                    self.export_relatorio_mapa(layer_comp.name())
                    # self.export_relatorio_vertices()
                    QgsProject.instance().removeMapLayer(print_lyr.id())
                    self.remover_camadas("Interseções")
                    self.merge_pdf()
                    self.remover_camadas("Vértices")
                self.update_progress_bar()

            for layer_comp in self.dic_layers_ever['db']:
                self.lyr_comp_geometry = lyr_utils.get_general_geom_type_name(layer_comp)
                if feature.attribute(layer_comp.name()) == True:
                    print_lyr = layer_comp.clone()
                    QgsProject.instance().addMapLayer(print_lyr)
                    self.handle_layers(self.dic_layers_ever, layer_comp.name())
                    self.adiciona_camada_vertices()
                    self.project_layers = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
                    self.export_relatorio_mapa(layer_comp.name())
                    # self.export_relatorio_vertices()
                    QgsProject.instance().removeMapLayer(print_lyr.id())
                    self.remover_camadas("Interseções")
                    self.merge_pdf()
                    self.remover_camadas("Vértices")
                self.update_progress_bar()

            for layer_comp in self.dic_layers_ever['wfs']:
                self.lyr_comp_geometry = lyr_utils.get_general_geom_type_name(layer_comp)
                if feature.attribute(layer_comp.name()) == True:
                    print_lyr = layer_comp.clone()
                    QgsProject.instance().addMapLayer(print_lyr)
                    self.handle_layers(self.dic_layers_ever, layer_comp.name())
                    self.adiciona_camada_vertices()
                    self.project_layers = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
                    self.export_relatorio_mapa(layer_comp.name())
                    # self.export_relatorio_vertices()
                    QgsProject.instance().removeMapLayer(print_lyr.id())
                    self.remover_camadas("Interseções")
                    self.merge_pdf()
                    self.remover_camadas("Vértices")
                self.update_progress_bar()
        
    def handle_layers(self, data, lyr_comp_name):
        lyr_overlay_point = data['lyr_overlap_point'] if 'lyr_overlap_point' in data else None
        lyr_overlay_line = data['lyr_overlap_line'] if 'lyr_overlap_line' in data else None
        lyr_overlay_polygon = data['lyr_overlap_polygon'] if 'lyr_overlap_polygon' in data else None

        overlay_layer_polygon = QgsVectorLayer("Polygon?crs=EPSG:4326", NOME_CAMADA_INTERSECAO_POLIGONO, "memory")
        provider_polygon = overlay_layer_polygon.dataProvider()
        overlay_layer_line = QgsVectorLayer("LineString?crs=EPSG:4326", NOME_CAMADA_INTERSECAO_LINHA, "memory")
        provider_line = overlay_layer_line.dataProvider()
        overlay_layer_point = QgsVectorLayer("Point?crs=EPSG:4326", NOME_CAMADA_INTERSECAO_PONTO, "memory")
        provider_point = overlay_layer_point.dataProvider()
        
        if QgsWkbTypes.displayString(self.feature.geometry().wkbType()) in CAMADA_DE_POLIGONO:
            if self.lyr_comp_geometry in CAMADA_DE_POLIGONO:
                if lyr_overlay_polygon and lyr_overlay_polygon.featureCount() > 0:
                    for feature_overlay in lyr_overlay_polygon.getFeatures():
                        if feature_overlay.attribute('Camada_sobreposicao') == lyr_comp_name and feature_overlay.attribute('logradouro') == self.feature.attribute('logradouro'):
                            nova_feature = QgsFeature()
                            nova_feature.setGeometry(feature_overlay.geometry())
                            provider_polygon.addFeatures([nova_feature])
                    overlay_layer_polygon = lyr_utils.lyr_process(overlay_layer_polygon, self.operation_config, CRS_PADRAO)
                    QgsProject.instance().addMapLayer(overlay_layer_polygon)

            elif self.lyr_comp_geometry in CAMADA_DE_LINHA:
                if lyr_overlay_line and lyr_overlay_line.featureCount() > 0:
                    for feature_overlay in lyr_overlay_line.getFeatures():
                        if feature_overlay.attribute('Camada_sobreposicao') == lyr_comp_name and feature_overlay.attribute('logradouro') == self.feature.attribute('logradouro'):
                            nova_feature = QgsFeature()
                            nova_feature.setGeometry(feature_overlay.geometry())
                            provider_line.addFeatures([nova_feature])
                    overlay_layer_line = lyr_utils.lyr_process(overlay_layer_line, self.operation_config, CRS_PADRAO)
                    QgsProject.instance().addMapLayer(overlay_layer_line)

            elif self.lyr_comp_geometry in CAMADA_DE_PONTO:
                if lyr_overlay_point and lyr_overlay_point.featureCount() > 0:
                    for feature_overlay in lyr_overlay_point.getFeatures():
                        if feature_overlay.attribute('Camada_sobreposicao') == lyr_comp_name and feature_overlay.attribute('logradouro') == self.feature.attribute('logradouro'):
                            nova_feature = QgsFeature()
                            nova_feature.setGeometry(feature_overlay.geometry())
                            provider_point.addFeatures([nova_feature])
                    overlay_layer_point = lyr_utils.lyr_process(overlay_layer_point, self.operation_config, CRS_PADRAO)
                    QgsProject.instance().addMapLayer(overlay_layer_point)

        elif QgsWkbTypes.displayString(self.feature.geometry().wkbType()) in CAMADA_DE_LINHA:
            if self.lyr_comp_geometry in CAMADA_DE_POLIGONO:
                if lyr_overlay_line and lyr_overlay_line.featureCount() > 0:
                    for feature_overlay in lyr_overlay_line.getFeatures():
                        if feature_overlay.attribute('Camada_sobreposicao') == lyr_comp_name and feature_overlay.attribute('logradouro') == self.feature.attribute('logradouro'):
                            nova_feature = QgsFeature()
                            nova_feature.setGeometry(feature_overlay.geometry())
                            provider_line.addFeatures([nova_feature])
                    overlay_layer_line = lyr_utils.lyr_process(overlay_layer_line, self.operation_config, CRS_PADRAO)
                    QgsProject.instance().addMapLayer(overlay_layer_line)
            elif self.lyr_comp_geometry in CAMADA_DE_LINHA:
                if lyr_overlay_point and lyr_overlay_point.featureCount() > 0:
                    for feature_overlay in lyr_overlay_point.getFeatures():
                        if feature_overlay.attribute('Camada_sobreposicao') == lyr_comp_name and feature_overlay.attribute('logradouro') == self.feature.attribute('logradouro'):
                            nova_feature = QgsFeature()
                            nova_feature.setGeometry(feature_overlay.geometry())
                            provider_point.addFeatures([nova_feature])
                    overlay_layer_point = lyr_utils.lyr_process(overlay_layer_point, self.operation_config, CRS_PADRAO)
                    QgsProject.instance().addMapLayer(overlay_layer_point)

        elif QgsWkbTypes.displayString(self.feature.geometry().wkbType()) in CAMADA_DE_PONTO:
                if lyr_overlay_point:
                    for feature_overlay in lyr_overlay_point.getFeatures():
                        if feature_overlay.attribute('Camada_sobreposicao') == lyr_comp_name and feature_overlay.attribute('logradouro') == self.feature.attribute('logradouro'):
                            nova_feature = QgsFeature()
                            nova_feature.setGeometry(feature_overlay.geometry())
                            provider_point.addFeatures([nova_feature])
                    overlay_layer_point = lyr_utils.lyr_process(overlay_layer_point, self.operation_config, CRS_PADRAO)
                    QgsProject.instance().addMapLayer(overlay_layer_point)
        
        
    # Remove camadas de interseções ou camadas de vértices/quotas já utilizadas
    def remover_camadas(self, type):
        camadas = QgsProject.instance().mapLayers().values()
        nomes_camadas_remover = ["Interseções (Polígono)", "Interseções (Linha)", "Interseções (Ponto)"] if type == "Interseções" else [NOME_CAMADA_VERTICES, NOME_CAMADA_QUOTAS]

        for camada in camadas:
            if camada.name() in nomes_camadas_remover:
                QgsProject.instance().removeMapLayer(camada)

    def adiciona_camada_vertices(self):
        lyr_vertices = self.dic_layers_ever['lyr_vertices'] if 'lyr_vertices' in self.dic_layers_ever else None
        lyr_quotas = self.dic_layers_ever['lyr_quotas'] if 'lyr_quotas' in self.dic_layers_ever else None
        
        if lyr_vertices:
            QgsProject.instance().addMapLayer(lyr_vertices.clone())
        if lyr_quotas:
            QgsProject.instance().addMapLayer(lyr_quotas.clone())

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
            if layer_item not in ('input', 'input_buffer', 'lyr_vertices', 'lyr_quotas', 'lyr_overlap_point', 'lyr_overlap_line', 'lyr_overlap_polygon'):
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
            
        self.handle_text_sintese(layout)

        lyr_utils.export_atlas_single_page(self.lyr_input, self.feature, layout_name, self.pdf_name, self.path_output, f'{self.time}_A_Relatorio')

    def export_relatorio_mapa(self, layer_name):
        layout_name = 'Planta_FolhaA3_Paisagem'
        layout = QgsProject.instance().layoutManager().layoutByName(layout_name)

        item_nao_homologada = layout.itemById('CD_Compl_Obs4')
        item_area_nao_homologada = layout.itemById('CD_Compl_Obs5')

        main_map = layout.itemById('Planta_Principal')
        localization_map = layout.itemById('Planta_Localizacao')
        crs = QgsCoordinateReferenceSystem(int(self.feature.attribute('EPSG_S2000')))
        main_map.setCrs(crs)
        main_map.refresh()
        localization_map.setCrs(crs)
        localization_map.refresh()

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
        if QgsWkbTypes.displayString(self.feature.geometry().wkbType()) in CAMADA_DE_POLIGONO:
            overlay_uniao_area.setText(f"Área de sobreposição com {layer_name}: 0,00 m².")
        elif QgsWkbTypes.displayString(self.feature.geometry().wkbType()) in CAMADA_DE_LINHA:
            overlay_uniao_area.setText(f"Sobreposição com {layer_name}: 0,00 m.")
        elif QgsWkbTypes.displayString(self.feature.geometry().wkbType()) in CAMADA_DE_PONTO:
            overlay_uniao_area.setText("")
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
                    if lyr_utils.get_general_geom_type_name(get_overlay_area) in CAMADA_DE_POLIGONO:
                        overlay_uniao_area.setText(f"Área de sobreposição com {layer_name}: " + str(self.overlay_analisys.calcular_soma_areas(get_overlay_area, self.feature.attribute('EPSG_S2000'))) + " m².")
                    elif lyr_utils.get_general_geom_type_name(get_overlay_area) in CAMADA_DE_LINHA:
                        overlay_uniao_area.setText(f"Sobreposição com {layer_name}: " + str(self.overlay_analisys.calcular_soma_areas(get_overlay_area, self.feature.attribute('EPSG_S2000'))) + " m.")
                    elif lyr_utils.get_general_geom_type_name(get_overlay_area) in CAMADA_DE_PONTO:
                        overlay_uniao_area.setText(f"")
            
            if layer_name == "Área Homologada":
                overlay_area_nao_homologada = self.overlay_nao_homologada()

                item_nao_homologada.setText("Lote não sobrepõe Área não Homologada")
                if "Área não Homologada" in column_value:
                    item_nao_homologada.setText("Lote sobrepõe Área não Homologada")
                
                if lyr_utils.get_general_geom_type_name(overlay_area_nao_homologada) in CAMADA_DE_POLIGONO:
                    item_area_nao_homologada.setText(f"Área de sobreposição com Área não Homologada: " + str(self.overlay_analisys.calcular_soma_areas(overlay_area_nao_homologada, self.feature.attribute('EPSG_S2000'))) + " m².")
                elif lyr_utils.get_general_geom_type_name(overlay_area_nao_homologada) in CAMADA_DE_LINHA:
                    item_area_nao_homologada.setText(f"Sobreposição com Área não Homologada: " + str(self.overlay_analisys.calcular_soma_areas(overlay_area_nao_homologada, self.feature.attribute('EPSG_S2000'))) + " m.")
                elif lyr_utils.get_general_geom_type_name(overlay_area_nao_homologada) in CAMADA_DE_PONTO:
                    item_area_nao_homologada.setText(f"")
                # item_area_nao_homologada.setText(f"Sobreposição Área não Homologada: {overlay_area_nao_homologada} m.")


        self.handle_text_mapa(layout)
        iface.mapCanvas().refresh()
        main_map = layout.itemById('Planta_Principal')
        main_map.refresh()
        lyr_utils.export_atlas_single_page(self.lyr_input, self.feature, layout_name, self.pdf_name, self.path_output, f'{self.time}_B_Mapa')

        if item_nao_homologada != None and item_area_nao_homologada != None:
            item_nao_homologada.setText("")
            item_area_nao_homologada.setText("")

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

    def handle_text_mapa(self, layout):
        """
        Faz a manipulação de alguns dados textuais presentes no layout de impressão no relatório de mapa.

        @keyword layout: Variável que armazena o objeto de manipulação do layout de relatório de mapa.
        """
        et = EnvTools()
        headers = et.get_report_hearder()

        spu = layout.itemById('CD_UnidadeSPU')
        spu.setText(headers['superintendencia'])

        sector = layout.itemById('CD_SubUnidadeSPU')
        sector.setText(headers['setor'])

        self.fill_data_source(layout)

    def handle_text_sintese(self, layout):
        """
        Faz a manipulação de alguns dados textuais presentes no layout de impressão no relatório síntese.

        @keyword layout: Variável que armazena o objeto de manipulação do layout de relatório síntese
        """
        et = EnvTools()
        headers = et.get_report_hearder()

        ministerio = layout.itemById('CD_Cabecalho_Ministerio')
        ministerio.setText(headers['ministerio'])

        secretaria_especial = layout.itemById('CD_Cabecalho_Secretaria_Esp')
        secretaria_especial.setText(headers['secretariaEspecial'])

        secretaria = layout.itemById('CD_Cabecalho_Secretaria')
        secretaria.setText(headers['secretaria'])

        superintendencia = layout.itemById('CD_Cabecalho_Superintendencia')
        superintendencia.setText(headers['superintendencia'])

        setor = layout.itemById('CD_Cabecalho_Setor')
        setor.setText(headers['setor'])

    def fill_data_source(self, layout):
        prisma_layers = [
            'Feição de Estudo (padrão)',
            'Feição de Estudo (Buffer)',
            'Feição de Estudo',
            'Interseções (Polígono)',
            'Interseções (Linha)',
            'Interseções (Ponto)',
            NOME_CAMADA_VERTICES,
            NOME_CAMADA_QUOTAS,
            'Com_Sobreposicao',
            'Sem_Sobreposicao'
            ]
        field_data_source = layout.itemById('CD_FonteDados')

        all_layers = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
        print_layers = [value for value in all_layers if value not in prisma_layers]

        data_source = self.get_data_source(print_layers)

        text = ''
        for item in print_layers:
            if item != self.basemap_name:
                text_item = data_source[item][0] + " (" + data_source[item][1].split('/')[-1] +"), "
                if text_item not in text:
                    text += text_item

        text += self.basemap_name + " (" + self.current_year + ")."
        field_data_source.setText(text)

    def get_data_source(self, layers_name):
        data_source = {}
        for name in layers_name:
            for x in self.operation_config['shp']:
                if name == x['nomeFantasiaCamada']:
                    data_source[str(name)] = [x['orgaoResponsavel'], x['periodosReferencia']]

            for x in self.operation_config['wfs']:
                if name == x['nomeFantasiaCamada']:
                    data_source[str(name)] = [x['orgaoResponsavel'], x['periodosReferencia']]

            for x in self.operation_config['pg']:
                if 'nomeFantasiaCamada' in x:
                    if name == x['nomeFantasiaCamada']:
                        data_source[str(name)] = [x['orgaoResponsavel'], x['periodosReferencia']]

            for x in self.operation_config['obrigatorio']:
                if 'nomeFantasiaCamada' in x:
                    if name == x['nomeFantasiaCamada']:
                        data_source[str(name)] = [x['orgaoResponsavel'], x['periodosReferencia']]
                else:
                    for x_layers in x['nomeFantasiaCamada']:
                        if name == x_layers:
                            data_source[str(name)] = [x['orgaoResponsavel'], x['periodosReferencia']]

        return data_source
        
    def overlay_nao_homologada(self):
        get_nao_homologada = QgsProject.instance().mapLayersByName('Área não Homologada')
        if not get_nao_homologada:
            return 0.00
                
        nao_homologada = get_nao_homologada[0]
        overlay_geometries = []
        geom_feature = self.feature.geometry()
        
        for feat in nao_homologada.getFeatures():
            geom = feat.geometry()
            # Verificar se há interseção
            if geom_feature.intersects(geom):
                intersecao = geom_feature.intersection(geom)
                overlay_geometries.append(intersecao)
        
        # Criar um novo QgsVectorLayer em memória
        crs = nao_homologada.crs()
        mem_layer = None

        if QgsWkbTypes.displayString(self.feature.geometry().wkbType()) in CAMADA_DE_POLIGONO:
            mem_layer = QgsVectorLayer('Polygon?crs=' + crs.authid(), 'Interseções Não Homologada', 'memory')
        elif QgsWkbTypes.displayString(self.feature.geometry().wkbType()) in CAMADA_DE_LINHA:
            mem_layer = QgsVectorLayer('LineString?crs=' + crs.authid(), 'Interseções Não Homologada', 'memory')
        elif QgsWkbTypes.displayString(self.feature.geometry().wkbType()) in CAMADA_DE_PONTO:
            mem_layer = QgsVectorLayer('Point?crs=' + crs.authid(), 'Interseções Não Homologada', 'memory')

        mem_layer_data = mem_layer.dataProvider()
        
        # Adicionar as geometrias de interseção como novas features
        new_features = []
        for geom in overlay_geometries:
            new_feat = QgsFeature()
            new_feat.setGeometry(geom)
            new_features.append(new_feat)
        
        mem_layer_data.addFeatures(new_features)
        mem_layer.updateExtents()
        
        # total_overlay = self.overlay_analisys.calcular_soma_areas(mem_layer, self.feature.attribute('EPSG_S2000'))
        return mem_layer
    
    def update_progress_bar(self):
        self.actual_progress = self.actual_progress + 1
        actual_progress = self.actual_progress * 100 / self.total_comp
        self.progress_bar.setValue(math.ceil(actual_progress))

        # Força o processamento dos eventos da UI
        QApplication.processEvents()
    