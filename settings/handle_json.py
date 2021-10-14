import os
import json

# CLASSE PARA MANIPULAÇÃO DO ARQUIVO JSON DE CONFIGURAÇÃO
class HandleJson():
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.json_path = base_dir + "\settings\dbtabases.json"
        with open(self.json_path, 'r', encoding='utf8') as f:
            self.json_config = json.load(f)

    def HandleShapefile(self):
        shp_list = []

        for base, data in self.json_config.items():
            if(data['tipo'] == 'shp'):
                shp_list.append(data)

        return shp_list

if __name__ == '__main__':
    teste = HandleJson()

    teste.HandleShapefile()