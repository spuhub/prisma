import os
import json

class JsonTools:
    """
    Classe para Manipular o arquivo de configuração.
    """
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.json_path = base_dir + "/settings/config_Json/dbtabases.json"

    def get_json(self):
        """
        Retorna o Json de configuração.
        @return: Json de configuração
        """
        with open(self.json_path, 'r', encoding='utf8') as f:
            json_config = json.load(f)
            return json_config

    def get_config_shapefile(self):

        """
        Retorna uma lista com as configurações de bases em ShapeFile.
        @return: Lista com as configurações.
        """
        json_config = self.get_json()
        shp_list = []

        for base, data in json_config.items():
            if 'tipo' in data and data['tipo'] == 'shp':
                shp_list.append(data)

        return shp_list

    def get_config_database(self):
        """
        Retorna uma lista com as configurações de bases em PostgreSQL.
        @return: Lista com as configurações.
        """
        json_config = self.get_json()
        shp_list = []

        for base, data in json_config.items():
            if 'tipo' in data and data['tipo'] == 'pg':
                shp_list.append(data)

        return shp_list

    def get_config_required(self):
        required_list = []
        json_config = self.get_json()
        required_layers = json_config['obrigatorio']

        for key, data_required_layer in required_layers.items():
            for base, data_json in json_config.items():
                if data_required_layer[0] == base:
                    if data_json['tipo'] == 'pg':
                        data_json['tabelasCamadas'] = [data_required_layer[1]]
                        data_json['nomeFantasiaTabelasCamadas'] = [data_required_layer[2]]
                    else:
                        data_json['nomeFantasiaCamada'] = [data_required_layer[2]]
                    required_list.append(data_json)

        return required_list

    def insert_database_pg(self, db_json_conf):
        """
        Insere as configurações de um banco de dados PostgreSQL no Json.
        @param db_json_conf: Json com as configurações do banco de dados
        @return: retorna o id da base inserida
        """
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
        """
        Edita um base de dados no PostgreSQL cujo seu id é passado como parametro
        @param db_id: Id da base de dados a ser editada
        @param db_json_new_conf: Json contendo as novas configurações da base de dados
        @return: void
        """
        with open(self.json_path, 'r') as f:
            dados = json.load(f)

        dados[db_id] = db_json_new_conf
        dados[db_id]["id"] = db_id
        print("vixx", dados)
        with open(self.json_path, 'w') as f:
            json.dump(dados, f, indent=4)

    def get_keys_name_source_data(self):

        """
        Retorna os nomes de todas as bases de dados (PG/SHP) dentro do JSON de Configuração
        @return: Json de com os nomes
        """

        source_data = {}
        with open(self.json_path, 'r') as f:
            dados = json.load(f)

        numofItens = list(dados.keys())

        for item in numofItens:
            nome = dados[item]["nome"]
            source_data[item] = nome

        return source_data

    def get_source_data(self, id_base):
        """
        Rettorna as configurações de uma fonte de dados apartir de seu ID
        @param id_base: Id da base de dados (postgresql ou SHP)
        @return: Json com as configurações de base de dados
        """
        with open(self.json_path, 'r') as f:
            dados = json.load(f)

    def get_camadas_base_obrigatoria (self):
        """
        Retorna todas as camadas obrigatórias.
        @return: Json com as camadas obigatórias
        """
        config = {}
        config["lpm_homologada"] = ["","",""]
        config["ltm_homologada"]  = ["","",""]
        config["area_homologada"]  = ["","",""]
        config["lpm_nao_homologada"]  = ["","",""]
        config["ltm_nao_homologada"]  = ["","",""]
        config["area_nao_homologada"] = ["","",""]

        with open(self.json_path, 'r') as f:
            dados = json.load(f)
        if "obrigatorio" in dados:
            return dados["obrigatorio"]
        else:
            return config

    def set_camadas_base_obrigatoria (self, new_conf):
        """
        Edita o valor de uma camada obigratria
        @param new_conf: ´Json coma as nova configurações de valor : {<Tipo camada> : {nome da base, nome da camada }}
        @return:
        """
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
