from ..settings.json_tools import JsonTools

class OperationController:
    def __init__(self):
        self.json_tools = JsonTools()
        self.data_bd = self.json_tools.get_config_database()
        self.data_shp = self.json_tools.get_config_shapefile()

    def get_operation(self, operation_config, selected_items_shp, selected_items_bd):
        if (operation_config['operation'] == 'shapefile'):
            operation_config = self.create_operation_config(operation_config, selected_items_bd, selected_items_shp)

            return operation_config

        elif (self.operation_config['operation'] == 'feature'):
            pass

        elif (self.operation_config['operation'] == 'address'):
            pass

        else:
            # Point
            pass

    # Monta uma lista de configurações para operação que será realizada
    def create_operation_config(self, operation_config, selected_items_bd, selected_items_shp):
        operation_config['shp'] = []
        for i in self.data_shp:
            if(i['nome'] in selected_items_shp):
                operation_config['shp'].append(i)

        operation_config['pg'] = []
        for i in self.data_bd:
            if (i['nome'] in selected_items_bd):
                operation_config['pg'].append(i)

        return operation_config