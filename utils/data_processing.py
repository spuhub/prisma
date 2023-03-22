from ..databases.db_connection import DbConnection
from ..databases.handle_selections import HandleSelections
from .utils import Utils
from .lyr_utils import *
from qgis.core import QgsVectorFileWriter
from ..environment import CAMADA_ENTRADA, CAMADA_ENTRADA_BUFFER, CRS_PADRAO

class DataProcessing():
    def __init__(self):
        """Método construtor da classe."""
        self.handle_selections = HandleSelections()
        self.utils = Utils()

    def data_preprocessing(self, operation_config):
        # Leitura do shapefile de input
        lyr_input = operation_config['input']
        lyr_input.setName(CAMADA_ENTRADA)
        lyr_input = lyr_process(lyr_input, CRS_PADRAO)
        lyr_input = add_style(lyr_input, "C:\\Users\\vinir\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\SPU-Prisma\\styles\\3_2_2_Trecho_Terreno_Marinha_A.sld")
        input_buffer = operation_config.get('aproximacao', {}).get('input', {})

        # Leitura de itens de comparação
        dic_lyr_retorno = {}
  
        list_required, operation_config = self.handle_selections.read_required_layers(operation_config['obrigatorio'], operation_config)
        list_selected_shp, operation_config = self.handle_selections.read_selected_shp(operation_config['shp'], operation_config)
        list_selected_wfs, operation_config = self.handle_selections.read_selected_wfs(operation_config['wfs'], operation_config)
        list_selected_db, operation_config = self.handle_selections.read_selected_db(operation_config['pg'], operation_config)

        # Adiciona buffer nas camadas de comparação
        for layer in list_selected_shp:
            if operation_config.get('aproximacao') and operation_config['aproximacao'].get(layer.name()):
                buffer_size = operation_config['aproximacao'][layer.name()]
                buffer_size = buffer_size if isinstance(buffer_size, int) else buffer_size[0]

                layer = insert_buffer(layer, buffer_size)

        for layer in list_selected_wfs:
            if operation_config.get('aproximacao') and operation_config['aproximacao'].get(layer.name()):
                buffer_size = operation_config['aproximacao'][layer.name()]
                buffer_size = buffer_size if isinstance(buffer_size, int) else buffer_size[0]

                layer = insert_buffer(layer, buffer_size)

        for layer in list_selected_db:
            if operation_config.get('aproximacao') and operation_config['aproximacao'].get(layer.name()):
                buffer_size = operation_config['aproximacao'][layer.name()]
                buffer_size = buffer_size if isinstance(buffer_size, int) else buffer_size[0]

                layer = insert_buffer(layer, buffer_size)

        for layer in list_required:
            if operation_config.get('aproximacao') and operation_config['aproximacao'].get(layer.name()):
                buffer_size = operation_config['aproximacao'][layer.name()]
                buffer_size = buffer_size if isinstance(buffer_size, int) else buffer_size[0]

                layer = insert_buffer(layer, buffer_size)

        dic_lyr_retorno = {'input': lyr_input, 'required': list_required, 'db': list_selected_db, 'shp': list_selected_shp, 'wfs': list_selected_wfs}
        
        # Trata o retorno da função caso usuário tenha inserido buffer na camada de entrada
        if input_buffer:
            lyr_input_buffer = insert_buffer(lyr_input, input_buffer)
            lyr_input_buffer.setName(CAMADA_ENTRADA_BUFFER)
            dic_lyr_retorno.update(input_buffer = lyr_input_buffer)

        return dic_lyr_retorno