# -*- coding: utf-8 -*-
import os

from qgis.core import QgsProject, QgsVectorFileWriter, QgsVectorLayer, QgsVectorDataProvider, QgsField, QgsFeature
from PyQt5 import QtCore
from ..utils import lyr_utils

class LayoutManager():
    """Classe responsável por fazer a manipulação do Layout de impressão. 
    Contém métodos para fazer o controle das feições carregadas para impressão,
    manipular textos e também algumas operações com dados que serão plotados ou 
    utilizados para gerar relatórios PDF.

    """

    def __init__(self, data, progress_bar):

        self.dic_layers = data['layers']
        self.possui_buffer = True if (('aproximacao' in data['operation_config']['input']) and data['operation_config']['input']['aproximacao'] > 0) else False
        self.lyr_input = self.dic_layers['input_buffer'] if self.possui_buffer else self.dic_layers['input']
        self.operation_config = data['operation_config']
        self.path_output = data['path_output']
        self.progress_bar = progress_bar
        self.path_gpkg = os.path.join(os.path.dirname(__file__), 'layouts', 'Camadas', 'base_projeto.gpkg')
        self.projeto_qgz = os.path.join(os.path.dirname(__file__), 'layouts', 'SPU-PRISMA_2.0_atlas.qgz')
        
        self.identifica_info_sobrep()
        self.atualiza_gpkg_temp()
        self.export_relatorio_sintese()
        self.export_relatorio_mapa()
        
    def atualiza_gpkg_temp(self):
        for layer_item in self.dic_layers:
            
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer 
            layer = self.dic_layers[layer_item]

            if isinstance(layer , QgsVectorLayer):
                options.layerName = layer.name()
                writer = QgsVectorFileWriter.writeAsVectorFormat(layer, self.path_gpkg , options)
                writer = None
            else:
                for idx, item in enumerate(layer):
                    options.layerName = item.name()
                    writer = QgsVectorFileWriter.writeAsVectorFormat(self.dic_layers[layer_item][idx], self.path_gpkg , options)
                    writer = None
                                        
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

        

        for layer_item in self.dic_layers:
            if layer_item not in ('input', 'input_buffer', 'lyr_overlap'):
                list_type = self.dic_layers[layer_item]
                for idx, layer in enumerate(list_type):
                    for feature in self.lyr_input.getFeatures():
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

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer 
        options.layerName = lyr_com_sobrep.name()
        writer = QgsVectorFileWriter.writeAsVectorFormat(lyr_com_sobrep, self.path_gpkg , options)
        writer = None
        options.layerName = lyr_sem_sobrep.name()
        writer = QgsVectorFileWriter.writeAsVectorFormat(lyr_sem_sobrep, self.path_gpkg , options)
        writer = None

    def export_relatorio_sintese(self):
        project = QgsProject.instance().read(self.projeto_qgz)
        layout = 'Relatorio_FolhaA4_Retrato'
        lyr_utils.export_atlas_single_page(self.lyr_input, layout, self.path_output, 'Relatorio')

    def export_relatorio_mapa(self):
        project = QgsProject.instance().read(self.projeto_qgz)
        layout = 'Planta_FolhaA3_Paisagem'
        lyr_utils.export_atlas_single_page(self.lyr_input, layout, self.path_output, 'Mapa')