import os
import json

class JsonTools:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.json_path = base_dir + "/settings/config_Json/dbtabases.json"
        with open(self.json_path, 'r', encoding='utf8') as f:
            self.json_config = json.load(f)

    def get_json(self):
        return self.json_config

    def get_config_shapefile(self):
        shp_list = []

        for base, data in self.json_config.items():
            if 'tipo' in data and data['tipo'] == 'shp':
                shp_list.append(data)

        return shp_list

    def get_config_database(self):
        shp_list = []

        for base, data in self.json_config.items():
            if 'tipo' in data and data['tipo'] == 'pg':
                shp_list.append(data)

        return shp_list

    def get_config_required(self):
        required_list = []

        required_layers = self.json_config['obrigatorio']

        for key, data_required_layer in required_layers.items():
            for base, data_json in self.json_config.items():
                if data_required_layer[0] == base:
                    if data_json['tipo'] == 'pg':
                        data_json['tabelasCamadas'] = [data_required_layer[1]]
                        data_json['nomeFantasiaTabelasCamadas'] = [data_required_layer[2]]
                    else:
                        data_json['nomeFantasiaCamada'] = [data_required_layer[2]]
                    required_list.append(data_json)

        return required_list

    def insert_database_pg(self, db_json_conf):
        dados = {}

        with open(self.json_path, 'r') as f:
            dados = json.load(f)

        numofItens = len(list(dados.keys()))

        dbid = "base" + str(numofItens + 1)
        db_json_conf["id"] = dbid

        dados[dbid] = db_json_conf
        with open(self.json_path, 'w') as f:
            json.dump(dados, f, indent=4)

        return dbid

    def edit_database(self, db_id, db_json_new_conf):
        with open(self.json_path, 'r') as f:
            dados = json.load(f)

        dados[db_id] = db_json_new_conf
        dados[db_id]["id"] = db_id
        print("vixx", dados)
        with open(self.json_path, 'w') as f:
            json.dump(dados, f, indent=4)

    def get_keys_name_source_data(self):

        source_data = {}
        with open(self.json_path, 'r') as f:
            dados = json.load(f)

        numofItens = list(dados.keys())

        for item in numofItens:
            nome = dados[item]["nome"]
            source_data[item] = nome

        return source_data

    def get_source_data(self, id_base):
        with open(self.json_path, 'r') as f:
            dados = json.load(f)

    def get_camadas_base_obrigatoria (self):
        with open(self.json_path, 'r') as f:
            dados = json.load(f)
        if "obrigatorio" in dados:
            return dados["obrigatorio"]
        else:
            return {}

    def set_camadas_base_obrigatoria (self, new_conf):
        with open(self.json_path, 'r') as f:
            dados = json.load(f)
        dados["obrigatorio"] = new_conf

        with open(self.json_path, 'w') as f:
            json.dump(dados, f, indent=4)

if __name__ == '__main__':
    d = JsonTools()

    saida = d.get_config_database()
    d.insert_database_pg(saida[0])
    print(d.get_config_database())
    print(d.get_config_shapefile())
