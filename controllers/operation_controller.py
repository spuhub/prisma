from ..settings.json_tools import JsonTools
from ..settings.env_tools import EnvTools

class OperationController:
    """
    Classe responsável por criar um dicionário contendo as configurações e especificações 
    necessárias para a operação de análise de sobreposição.

    Especificações incluem o tipo de operação (shapefile, ponto, endereço, feição selecionada),
    arquivos shapefile e bases de dados selecionados para comparação.

    Atributos:
        data_bd (list): Lista contendo bases de dados configuradas no arquivo JSON.
        data_shp (list): Lista contendo shapefiles configurados no arquivo JSON.
        data_wfs (list): Lista contendo camadas WFS configuradas no arquivo JSON.
        data_required (list): Lista contendo camadas obrigatórias configuradas no arquivo JSON.
        basemap (list): Lista de mapas base configurados no arquivo JSON.
        style_default_layers (list): Lista de estilos padrão para camadas configurados no arquivo JSON.
        json_tools (JsonTools): Classe para manipulação de arquivos JSON.
    """
    def __init__(self):
        """
        Inicializa a classe OperationController e carrega as configurações de bases de dados,
        shapefiles, WFS, camadas obrigatórias, mapas base e estilos padrão a partir do arquivo JSON.
        """
        self.json_tools = JsonTools()
        self.data_bd = self.json_tools.get_config_database()
        self.data_shp = self.json_tools.get_config_shapefile()
        self.data_wfs = self.json_tools.get_config_wfs()
        self.data_required = self.json_tools.get_config_required()
        self.basemap = self.json_tools.get_config_basemap()
        self.style_default_layers = self.json_tools.get_config_style_default_layers()

    def get_operation(self, operation_config, selected_items_shp, selected_items_wfs, selected_items_bd):
        """
        Gera as configurações da operação de busca de sobreposição.

        Args:
            operation_config (dict): Configurações básicas da operação.
            selected_items_shp (list): Lista de shapefiles selecionados para comparação.
            selected_items_wfs (list): Lista de camadas WFS selecionadas para comparação.
            selected_items_bd (list): Lista de bases de dados selecionadas para comparação.

        Returns:
            dict: Dicionário contendo as especificações completas da operação.
        """
        if (operation_config['operation'] == 'shapefile'):
            operation_config = self.create_operation_config(operation_config, selected_items_bd, selected_items_wfs, selected_items_shp)

        elif (operation_config['operation'] == 'feature'):
            operation_config = self.create_operation_config(operation_config, selected_items_bd, selected_items_wfs, selected_items_shp)

        elif (operation_config['operation'] == 'coordinate'):
            operation_config = self.create_operation_config(operation_config, selected_items_bd, selected_items_wfs, selected_items_shp)

        if len(self.basemap) > 0:
            operation_config['basemap'] = self.basemap

        operation_config['style_default_layers'] = self.style_default_layers

        return operation_config

    def create_operation_config(self, operation_config, selected_items_bd, selected_items_wfs, selected_items_shp):
        """
        Monta o dicionário de configurações detalhadas para a operação a ser realizada.

        Args:
            operation_config (dict): Configurações básicas da operação.
            selected_items_bd (list): Lista de bases de dados selecionadas para comparação.
            selected_items_wfs (list): Lista de camadas WFS selecionadas para comparação.
            selected_items_shp (list): Lista de shapefiles selecionados para comparação.

        Returns:
            dict: Dicionário contendo as configurações detalhadas da operação.
        """
        operation_config['shp'] = []
        for i in self.data_shp:
            if(i['nome'] in selected_items_shp):
                operation_config['shp'].append(i)

        operation_config['wfs'] = []

        handled_items_wfs = []
        for value in selected_items_wfs:
            handled_value = value.replace(')', '').split(' (')
            handled_items_wfs.append(handled_value)

        for i in self.data_wfs:
            for key, layer in enumerate(i['nomeFantasiaCamada']):
                for layer_req in handled_items_wfs:
                    if i['nome'] == layer_req[1] and layer == layer_req[0]:
                        operation_config['wfs'].append(dict(i))
                        operation_config['wfs'][-1]['nomeFantasiaCamada'] = layer
                        operation_config['wfs'][-1]['tabelasCamadas'] = i['tabelasCamadas'][key]
                        operation_config['wfs'][-1]['estiloCamadas'] = i['estiloCamadas'][key]
                        operation_config['wfs'][-1]['aproximacao'] = i['aproximacao'][key]
                        operation_config['wfs'][-1]['diretorio'] = i['diretorio'][key]
                        operation_config['wfs'][-1]['orgaoResponsavel'] = i['orgaoResponsavel'][key]
                        operation_config['wfs'][-1]['periodosReferencia'] = i['periodosReferencia'][key]

        operation_config['pg'] = []

        handled_items_db = []
        for value in selected_items_bd:
            handled_value = value.replace(')', '').split(' (')
            handled_items_db.append(handled_value)

        for i in self.data_bd:
            et = EnvTools()
            login = et.get_credentials(i['id'])

            i['usuario'] = login[0]
            i['senha'] = login[1]

            for key, layer in enumerate(i['nomeFantasiaCamada']):
                for layer_req in handled_items_db:
                    if i['nome'] == layer_req[1] and layer == layer_req[0]:
                        operation_config['pg'].append(dict(i))
                        operation_config['pg'][-1]['nomeFantasiaCamada'] = layer
                        operation_config['pg'][-1]['tabelasCamadas'] = i['tabelasCamadas'][key]
                        operation_config['pg'][-1]['estiloCamadas'] = i['estiloCamadas'][key]
                        operation_config['pg'][-1]['aproximacao'] = i['aproximacao'][key]

        for i in self.data_required:
            if i['tipo'] == 'pg':
                for x in self.data_bd:
                    if i['id'] == x['id']:
                        et = EnvTools()
                        login = et.get_credentials(i['id'])

                        i['usuario'] = login[0]
                        i['senha'] = login[1]

        operation_config['obrigatorio'] = self.data_required

        return operation_config