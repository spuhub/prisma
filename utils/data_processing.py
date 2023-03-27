from qgis.core import QgsField, QgsFeatureRequest
from PyQt5.QtCore import QVariant

from ..databases.db_connection import DbConnection
from ..databases.handle_selections import HandleSelections
from .utils import Utils
from .lyr_utils import *

from ..environment import CAMADA_ENTRADA, CAMADA_ENTRADA_BUFFER, CRS_PADRAO

class DataProcessing():
    def __init__(self):
        """Método construtor da classe."""
        self.handle_selections = HandleSelections()
        self.utils = Utils()

    def data_preprocessing(self, operation_config):
        # Leitura do shapefile de input
        lyr_input = operation_config['input']['layer']
        lyr_input.setName(CAMADA_ENTRADA)
        lyr_input = lyr_process(lyr_input, operation_config, CRS_PADRAO)
        lyr_input = add_style(lyr_input, "C:\\Users\\vinir\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\SPU-Prisma\\styles\\3_2_2_Trecho_Terreno_Marinha_A.sld")
        input_buffer = operation_config['input'].get('aproximacao', {})

        # Leitura de itens de comparação
        dic_lyr_retorno = {}
  
        list_required, operation_config = self.handle_selections.read_required_layers(operation_config['obrigatorio'], operation_config)
        list_selected_shp, operation_config = self.handle_selections.read_selected_shp(operation_config['shp'], operation_config)
        list_selected_wfs, operation_config = self.handle_selections.read_selected_wfs(operation_config['wfs'], operation_config)
        list_selected_db, operation_config = self.handle_selections.read_selected_db(operation_config['pg'], operation_config)

        for layer in list_selected_shp:
            # Criar campo com o nome da camada de comparação
            lyr_input = self.init_field_layer_name(lyr_input, layer.name())
            # Adiciona buffer nas camadas de comparação
            if operation_config.get('aproximacao') and operation_config['aproximacao'].get(layer.name()):
                layer = insert_buffer(layer, operation_config['aproximacao'][layer.name()])

        for layer in list_selected_wfs:
            # Criar campo com o nome da camada de comparação
            lyr_input = self.init_field_layer_name(lyr_input, layer.name())
            # Adiciona buffer nas camadas de comparação
            if operation_config.get('aproximacao') and operation_config['aproximacao'].get(layer.name()):
                layer = insert_buffer(layer, operation_config['aproximacao'][layer.name()])

        for layer in list_selected_db:
            # Criar campo com o nome da camada de comparação
            lyr_input = self.init_field_layer_name(lyr_input, layer.name())
            # Adiciona buffer nas camadas de comparação
            if operation_config.get('aproximacao') and operation_config['aproximacao'].get(layer.name()):
                layer = insert_buffer(layer, operation_config['aproximacao'][layer.name()])

        for layer in list_required:
            # Criar campo com o nome da camada de comparação
            lyr_input = self.init_field_layer_name(lyr_input, layer.name())
            # Adiciona buffer nas camadas de comparação
            if operation_config.get('aproximacao') and operation_config['aproximacao'].get(layer.name()):
                layer = insert_buffer(layer, operation_config['aproximacao'][layer.name()])

        lyr_input.updateFields()
        dic_lyr_retorno = {'input': lyr_input, 'required': list_required, 'db': list_selected_db, 'shp': list_selected_shp, 'wfs': list_selected_wfs}
        
        # Trata o retorno da função caso usuário tenha inserido buffer na camada de entrada
        if input_buffer:
            lyr_input_buffer = insert_buffer(lyr_input, input_buffer)
            lyr_input_buffer.setName(CAMADA_ENTRADA_BUFFER)
            dic_lyr_retorno.update(input_buffer = lyr_input_buffer)

        return dic_lyr_retorno
    
    def init_field_layer_name(self, layer, field_name):
        """
        Função que cria para um novo campo no shapefile de input.
        Esse campo tem o nome de uma das camadas de comparação, que armazenara True caso haja sobreposição
        e False caso não exista sobreposição entre feição de entrada e camada de comparação 

        @param layer: Camada de entrada
        @param field_name: Nome fantasia da camada de comparação
        """
        layer_provider = layer.dataProvider()
        # Adiciona um novo campo ao layer
        layer_provider.addAttributes([QgsField(field_name, QVariant.Bool)])

        # Atualiza os campos
        layer.updateFields()

        # Obtém o índice do novo campo
        field_index = layer.fields().indexFromName(field_name)

        # Cria um objeto QgsFeatureRequest para selecionar todos os recursos da camada
        request = QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)

        # Loop sobre todos os recursos da camada e atualiza o novo campo com o valor padrão
        for feat in layer.getFeatures(request):
            layer.changeAttributeValue(feat.id(), field_index, False)

        return layer