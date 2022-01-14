from ..settings.json_tools import JsonTools
from ..settings.env_tools import  EnvTools
from PyQt5.QtCore import QVariant

import geopandas as gpd

class OperationController:
    def __init__(self):
        self.json_tools = JsonTools()
        self.data_bd = self.json_tools.get_config_database()
        self.data_shp = self.json_tools.get_config_shapefile()

    def get_operation(self, operation_config, selected_items_shp, selected_items_bd):
        if (operation_config['operation'] == 'shapefile'):
            operation_config = self.create_operation_config(operation_config, selected_items_bd, selected_items_shp)

            return operation_config

        elif (operation_config['operation'] == 'feature'):
            operation_config = self.create_operation_config(operation_config, selected_items_bd, selected_items_shp)

            # Quando uma camada é pega do QGis, alguns campos são retornados em formato de objeto QVariant
            # Esses dados sempre são nulos e podem ser apagados, que é oq está sendo feito
            # Veja: https://github.com/geopandas/geopandas/issues/2269
            input = operation_config['input']
            columns = list(input)

            for i in range(len(input)):
                print("i: ", i)
                for column in columns:
                    if column in input:
                        if type(input.iloc[i][column]) == QVariant:
                            input = input.drop(column, axis=1)

            operation_config['input'] = input
            return operation_config

        elif (operation_config['operation'] == 'coordinate'):
            operation_config = self.create_operation_config(operation_config, selected_items_bd, selected_items_shp)

            return operation_config

    # Monta uma lista de configurações para operação que será realizada
    def create_operation_config(self, operation_config, selected_items_bd, selected_items_shp):
        operation_config['shp'] = []
        for i in self.data_shp:
            if(i['nome'] in selected_items_shp):
                operation_config['shp'].append(i)

        operation_config['pg'] = []
        for i in self.data_bd:
            et = EnvTools()
            login = et.get_credentials(i['id'])

            i['usuario'] = login[0]
            i['senha'] = login[1]

            if (i['nome'] in selected_items_bd):
                operation_config['pg'].append(i)

        return operation_config