# -*- coding: utf-8 -*-
import os

from qgis.core import  QgsVectorFileWriter, QgsVectorLayer

class LayoutManager():
    """Classe responsável por fazer a manipulação do Layout de impressão. 
    Contém métodos para fazer o controle das feições carregadas para impressão,
    manipular textos e também algumas operações com dados que serão plotados ou 
    utilizados para gerar relatórios PDF.


    """

    def __init__(self, data, progress_bar):

        self.dic_layers = data['layers']
        self.operation_config = data['operation_config']
        self.progress_bar = progress_bar
        self.path_gpkg = os.path.join(os.path.dirname(__file__), 'layouts', 'Camadas', 'base_projeto.gpkg')
        self.atualiza_gpkg_temp()
    
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