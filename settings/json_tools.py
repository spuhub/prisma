import os
import re
import json
from .env_tools import EnvTools

from typing import Optional

class JsonTools:
    """
    Classe responsável por manipular o arquivo de configuração JSON.

    Esta classe é utilizada para obter, inserir, editar e deletar informações armazenadas no 
    arquivo de configuração do sistema, incluindo configurações de bancos de dados, shapefiles, 
    WFS, camadas obrigatórias, e estilos padrão.

    Atributos:
        json_path (str): Caminho absoluto para o arquivo JSON de configuração.
    """
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env = EnvTools()
        current_path = env.get_path_json()
        self.json_path = base_dir + "/settings/config_Json/dbtabases.json"
        # if current_path != "" and current_path is not None and current_path != "None":
        #     self.json_path = current_path



    def get_json(self):
        """
        Retorna o conteúdo completo do arquivo JSON de configuração.

        Returns:
            dict: Dados do JSON de configuração. Retorna um dicionário vazio se o arquivo estiver vazio.
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
        Retorna as configurações de bases de dados do tipo Shapefile.

        Returns:
            list: Lista contendo as configurações de todas as bases do tipo Shapefile.
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
        Retorna as configurações de bases de dados do tipo PostgreSQL.

        Returns:
            list: Lista contendo as configurações de todas as bases PostgreSQL.
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
        Retorna as configurações de bases de dados do tipo WFS.

        Returns:
            list: Lista contendo as configurações de todas as bases WFS.
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
        Retorna as configurações das camadas obrigatórias do sistema.

        Returns:
            list: Lista contendo as configurações das camadas obrigatórias. Retorna uma lista vazia 
                se não existirem camadas obrigatórias configuradas.
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
                                data_json['nomeFantasiaCamada'] = data_required_layer[2]
                            else:
                                data_json['nomeFantasiaCamada'] = data_required_layer[2]
                            required_list.append(data_json)

        return required_list

    def insert_data(self, all_json):
        """
        Insere ou atualiza o conteúdo completo do arquivo JSON.

        Args:
            all_json (dict): Dicionário contendo os novos dados a serem salvos no arquivo JSON.
        """
        with open(self.json_path, "w") as f:
            json.dump(all_json, f, indent=4)
            f.close()

    def get_config_basemap(self):
        """
        Retorna as configurações dos mapas base (basemap).

        Returns:
            list: Lista contendo as configurações dos mapas base.
        """
        basemap_list = []

        if os.stat(self.json_path).st_size != 0:
            with open(self.json_path, 'r', encoding='utf8') as f:
                json_config = json.load(f)
                f.close()

        if 'basemap' in json_config:
            basemap_list = json_config['basemap']

        return basemap_list

    def get_config_style_default_layers(self):

        """
        Retorna uma lista com as configurações de estilo padrão.
        @return: Lista com as configurações.
        """
        style_default_layers_list = []

        if os.stat(self.json_path).st_size != 0:
            with open(self.json_path, 'r', encoding='utf8') as f:
                json_config = json.load(f)
                f.close()

        if 'style_default_layers' in json_config:
            style_default_layers_list = json_config['style_default_layers']

        return style_default_layers_list

    def insert_database_pg(self, db_json_conf, id_base: Optional[str] = None):
        """
        Insere ou atualiza as configurações de um banco de dados PostgreSQL no JSON.

        Args:
            db_json_conf (dict): Dicionário contendo as configurações do banco de dados.
            id_base (str, opcional): ID do banco de dados a ser atualizado. Caso seja None, 
                                    será gerado um novo ID.

        Returns:
            str: ID do banco de dados inserido ou atualizado.
        """
        dados = {}

        if os.stat(self.json_path).st_size != 0:

            with open(self.json_path, 'r') as f:
                dados = json.load(f)
                f.close()

            key = list(dados.keys())[-1]    
            dbid: str
            base_number = self.extrair_numeros(dados[key]['id']) if 'id' in dados[key] else [0]
            dbid = id_base or "base" + str(base_number[0] + 1)
            db_json_conf["id"] = dbid
            dados[dbid] = db_json_conf

        with open(self.json_path, 'w') as f:
            json.dump(dados, f, indent=4)
            f.close()

        return dbid

    def extrair_numeros(self, string):
        numeros = re.findall(r'\d+', string)
        return [int(numero) for numero in numeros]

    def edit_database(self, db_id, db_json_new_conf):
        """
        Edita as configurações de uma base de dados existente no JSON.

        Args:
            db_id (str): ID da base de dados a ser editada.
            db_json_new_conf (dict): Dicionário contendo as novas configurações da base de dados.
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
        Retorna todas as camadas obrigatórias configuradas no JSON.

        Returns:
            dict: Dicionário contendo as configurações das camadas obrigatórias.
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
        Atualiza as configurações das camadas obrigatórias no JSON.

        Args:
            new_conf (dict): Dicionário contendo as novas configurações das camadas obrigatórias.
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
        """
        Remove uma base de dados do JSON de configuração.

        Args:
            idConfig (str): ID da base de dados a ser removida.
        """
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
