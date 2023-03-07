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

        # Leitura de itens de comparação
        dic_lyr_retorno = {}
        list_required = self.handle_selections.read_required_layers(operation_config['obrigatorio'])
        list_selected_shp = self.handle_selections.read_selected_shp(operation_config['shp'])
        list_selected_wfs = self.handle_selections.read_selected_wfs(operation_config['wfs'])
        list_selected_db = self.handle_selections.read_selected_db(operation_config['pg'])

        # Adiciona buffer na camada de input
        lyr_input_buffer = insert_buffer(lyr_input, 100)
        lyr_input_buffer.setName("Input Buffer")

        # Adiciona buffer nas camadas de comparação
        for layer in list_selected_shp:
            layer = insert_buffer(layer, 100)

        for layer in list_selected_wfs:
            layer = insert_buffer(layer, 100)

        for layer in list_selected_db:
            layer = insert_buffer(layer, 100)

        dic_lyr_retorno = {'input_default': lyr_input, 'input_buffer': lyr_input_buffer, 'required': list_required, 'db': list_selected_db, 'shp': list_selected_shp, 'wfs': list_selected_wfs}

        return dic_lyr_retorno