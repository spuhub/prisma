import os
import json

from typing import Optional

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
        if os.stat(self.json_path).st_size == 0:
            return {}

        else:
            with open(self.json_path, 'r', encoding='utf8') as f:
                json_config = json.load(f)
                f.close()

            return json_config

    def get_config_shapefile(self):

        """
        Retorna uma lista com as configurações de bases em ShapeFile.
        @return: Lista com as configurações.
        """
        shp_list = []

        if os.stat(self.json_path).st_size != 0:
            with open(self.json_path, 'r', encoding='utf8') as f:
                json_config = json.load(f)
                f.close()

            for base, data in json_config.items():
                if 'tipo' in data and data['tipo'] == 'shp':
                    shp_list.append(data)

        return shp_list

    def get_config_database(self):

        """
        Retorna uma lista com as configurações de bases em PostgreSQL.
        @return: Lista com as configurações.

        """
        shp_list = []

        if os.stat(self.json_path).st_size == 0:
            return []
        else:
            with open(self.json_path, 'r', encoding='utf8') as f:
                json_config = json.load(f)
                f.close()

        for base, data in json_config.items():
            if 'tipo' in data and data['tipo'] == 'pg':
                shp_list.append(data)

        return shp_list

    def get_config_wfs(self):

        """
        Retorna uma lista com as configurações de bases em WFS.
        @return: Lista com as configurações.
        """
        wfs_list = []

        if os.stat(self.json_path).st_size != 0:
            with open(self.json_path, 'r', encoding='utf8') as f:
                json_config = json.load(f)
                f.close()

            for base, data in json_config.items():
                if 'tipo' in data and data['tipo'] == 'wfs':
                    wfs_list.append(data)

        return wfs_list

    def get_config_required(self):

        """
        Retorna uma lista com as configurações das camadas obrigatórias caso tiver. Se não tiver camadas
        obrigatórias retorna uma lista vazia.
        @return: Lista com as configurações.
        """

        required_list = []

        if os.stat(self.json_path).st_size == 0:
            return []
        else:
            with open(self.json_path, 'r', encoding='utf8') as f:
                json_config = json.load(f)
                f.close()

            if json_config == {}:
                return []

            if json_config != {}:
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

    def insert_data(self, all_json):
        with open(self.json_path, "w") as f:
            json.dump(all_json, f, indent=4)
            f.close()

    def get_config_basemap(self):

        """
        Retorna uma lista com as configurações de basemap.
        @return: Lista com as configurações.
        """
        basemap_list = []

        if os.stat(self.json_path).st_size != 0:
            with open(self.json_path, 'r', encoding='utf8') as f:
                json_config = json.load(f)
                f.close()

        if 'basemap' in json_config:
            basemap_list = json_config['basemap']

        return basemap_list

    def get_config_sld_default_layers(self):

        """
        Retorna uma lista com as configurações de sld_default_layers.
        @return: Lista com as configurações.
        """
        sld_default_layers_list = []

        if os.stat(self.json_path).st_size != 0:
            with open(self.json_path, 'r', encoding='utf8') as f:
                json_config = json.load(f)
                f.close()

        if 'sld_default_layers' in json_config:
            sld_default_layers_list = json_config['sld_default_layers']

        return sld_default_layers_list

    def insert_database_pg(self, db_json_conf, id_base: Optional[str] = None):
        """
        Insere as configurações de um banco de dados PostgreSQL no Json.
        @param db_json_conf: Json com as configurações do banco de dados
        @return: retorna o id da base inserida
        """
        dados = {}

        if os.stat(self.json_path).st_size != 0:

            with open(self.json_path, 'r') as f:
                dados = json.load(f)
                f.close()

            numofItens = len(list(dados.keys()))

            dbid = id_base or ("base" + str(numofItens + 1))
            db_json_conf["id"] = dbid
            dados[dbid] = db_json_conf

        with open(self.json_path, 'w') as f:
            json.dump(dados, f, indent=4)
            f.close()

        return dbid

    def edit_database(self, db_id, db_json_new_conf):
        """
        Edita um base de dados no PostgreSQL cujo seu id é passado como parametro
        @param db_id: Id da base de dados a ser editada
        @param db_json_new_conf: Json contendo as novas configurações da base de dados
        @return: void
        """
        if os.stat(self.json_path).st_size != 0:
            with open(self.json_path, 'r') as f:
                dados = json.load(f)
            f.close()

            dados[db_id] = db_json_new_conf
            dados[db_id]["id"] = db_id

            with open(self.json_path, 'w') as f:
                json.dump(dados, f, indent=4)
            f.close()

    def get_keys_name_source_data(self):

        """
        Retorna os nomes de todas as bases de dados (PG/SHP) dentro do JSON de Configuração
        @return: Json de com os nomes
        """

        if os.stat(self.json_path).st_size == 0:
            return {}
        else:
            with open(self.json_path, 'r', encoding='utf8') as f:
                dados = json.load(f)
                f.close()

                if dados == {}:
                    return {}
                if dados != {}:
                    source_data = {}
                    numofItens = list(dados.keys())

                    for item in numofItens:
                        if "nome" in dados[item]:
                            nome = dados[item]["nome"]
                            source_data[item] = nome

                    return source_data

    def get_source_data(self, id_base):
        """
        Rettorna as configurações de uma fonte de dados apartir de seu ID
        @param id_base: Id da base de dados (postgresql ou SHP)
        @return: Json com as configurações de base de dados
        """
        get_base: dict = {}
        with open(self.json_path, 'r') as f:
            dados = json.load(f)
            get_base = dados.get(str(id_base))
            f.close()

        return get_base

    def get_camadas_base_obrigatoria(self):
        """
        Retorna todas as camadas obrigatórias.
        @return: Json com os nomes das camadas obrigatórias
        """

        if os.stat(self.json_path).st_size == 0:
            return {}
        else:
            with open(self.json_path, 'r') as f:
                dados = json.load(f)
            f.close()
            if dados == {}:
                return {}
            else:
                if "obrigatorio" in dados:
                    return dados["obrigatorio"]
                else:
                    return {}

    def set_camadas_base_obrigatoria (self, new_conf):
        """
        Edita o valor de uma camada obigratria
        @param new_conf: ´Json coma as nova configurações de valor : {<Tipo camada> : {nome da base, nome da camada }}
        @return:
        """
        if os.stat(self.json_path).st_size == 0:
            return {}
        else:
            with open(self.json_path, 'r') as f:
                dados = json.load(f)
            f.close()
            if dados == {}:
                return {}
            else:
                dados["obrigatorio"] = new_conf

                with open(self.json_path, 'w') as f:
                    json.dump(dados, f, indent=4)
                f.close()

    def delete_base(self, idConfig):

        if os.stat(self.json_path).st_size != 0:

            with open(self.json_path, 'r') as f:
                dados = json.load(f)
                f.close()
            if dados != {}:
                if idConfig in dados:
                    del dados[idConfig]

                if "obrigatorio" in dados:
                    camadas_obrigatorias = dados["obrigatorio"]
                    key_camadas_obrigatorias = camadas_obrigatorias.keys()

                nome_camada_del = ""
                for camada in key_camadas_obrigatorias:
                    if camadas_obrigatorias[camada][0] == idConfig:
                        nome_camada_del = camada

                if nome_camada_del != "":
                    del camadas_obrigatorias[nome_camada_del]
                    dados["obrigatorio"] = camadas_obrigatorias

                with open(self.json_path, 'w') as f:
                    json.dump(dados, f, indent=4)
                    f.close()


if __name__ == '__main__':
    d = JsonTools()

    c = {"adada" : "amsi", "monte22333" : "mais"}
    b = {
        "lpm_homologada": [
            "base1",
            "faixa_dominio",
            "LPM Homologada"
        ]}
    #saida = d.get_config_database()
    # d.insert_database_pg(saida[0])
    print(d.delete_base("base3"))
    #print(d.get_config_shapefile())
