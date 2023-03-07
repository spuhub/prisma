from ..databases.db_connection import DbConnection
from ..databases.handle_selections import HandleSelections
from .utils import Utils
from .lyr_utils import *
from qgis.core import QgsVectorFileWriter

class DataProcessing():
    def __init__(self):
        """Método construtor da classe."""
        self.handle_selections = HandleSelections()
        self.utils = Utils()

    def data_preprocessing(self, operation_config):
        # Leitura do shapefile de input
        lyr_input = operation_config['input']
        lyr_input = lyr_process(lyr_input, 4326)
        input_buffer = operation_config.get('aproximacao', {}).get('input', {})

        # Leitura de itens de comparação
        dic_lyr_retorno = {}
        list_required = self.handle_selections.read_required_layers(operation_config['obrigatorio'])
        list_selected_shp = self.handle_selections.read_selected_shp(operation_config['shp'])
        list_selected_wfs = self.handle_selections.read_selected_wfs(operation_config['wfs'])
        list_selected_db = self.handle_selections.read_selected_db(operation_config['pg'])

        # Adiciona buffer na camada de input
        lyr_input_buffer = insert_buffer(lyr_input, 100)
        lyr_input_buffer.setName("Input Buffer")
        list_required, operation_config = self.handle_selections.read_required_layers(operation_config['obrigatorio'], operation_config)
        list_selected_shp, operation_config = self.handle_selections.read_selected_shp(operation_config['shp'], operation_config)
        list_selected_wfs, operation_config = self.handle_selections.read_selected_wfs(operation_config['wfs'], operation_config)
        list_selected_db, operation_config = self.handle_selections.read_selected_db(operation_config['pg'], operation_config)

        # Adiciona buffer nas camadas de comparação
        for layer in list_selected_shp:
            if operation_config.get('aproximacao') and operation_config['aproximacao'].get(layer.name()):
                layer = insert_buffer(layer, operation_config['aproximacao'][layer.name()][0])

        for layer in list_selected_wfs:
            if operation_config.get('aproximacao') and operation_config['aproximacao'].get(layer.name()):
                layer = insert_buffer(layer, operation_config['aproximacao'][layer.name()])

        for layer in list_selected_db:
            if operation_config.get('aproximacao') and operation_config['aproximacao'].get(layer.name()):
                layer = insert_buffer(layer, operation_config['aproximacao'][layer.name()])


        dic_lyr_retorno = {'input': lyr_input, 'required': list_required, 'db': list_selected_db, 'shp': list_selected_shp, 'wfs': list_selected_wfs}
        
        # Trata o retorno da função caso usuário tenha inserido buffer na camada de entrada
        if input_buffer:
            lyr_input_buffer = insert_buffer(lyr_input, input_buffer)
            dic_lyr_retorno.update(input = lyr_input_buffer, input_default = lyr_input)

        return dic_lyr_retorno