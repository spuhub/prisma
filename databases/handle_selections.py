from qgis.core import QgsVectorLayer, QgsDataSourceUri
from ..utils.lyr_utils import *

from ..environment import CRS_PADRAO

class HandleSelections():
    """
    Classe responsável por gerenciar a leitura de objetos selecionados para comparação, incluindo shapefiles, WFS e camadas de banco de dados.
    """
    def __init__(self):
        """
        Método de inicialização da classe.

        """

    def read_selected_shp(self, selected_shapefiles, operation_config):
        """
        Lê shapefiles selecionados para comparação e os processa no formato QgsVectorLayer.

        Args:
            selected_shapefiles (list): Lista contendo informações das bases de dados selecionadas, obtidas de um arquivo JSON.
            operation_config (dict): Configurações da operação em andamento.

        Returns:
            tuple: Uma lista com os shapefiles selecionados no formato QgsVectorLayer e o dicionário atualizado de configurações.
        """
        list_selected_shp = []

        # Cria uma lista com dados no formato QgsVectorLayer das áreas selecionadas para comparação
        for shp in range(len(selected_shapefiles)):
            arq_shp = selected_shapefiles[shp]['diretorioLocal']
            nome_shp = selected_shapefiles[shp]['nomeFantasiaCamada']
            lyr_shp = QgsVectorLayer(arq_shp, nome_shp, 'ogr')
            lyr_shp_reproj = lyr_process(lyr_shp, operation_config, CRS_PADRAO)
            lyr_shp_reproj.setName(nome_shp)
            list_selected_shp.append(lyr_shp_reproj)

            operation_config.setdefault('aproximacao', {})[nome_shp] = selected_shapefiles[shp]['aproximacao']

        return list_selected_shp, operation_config

    def read_selected_wfs(self, selected_wfs, operation_config):
        """
        Lê camadas WFS selecionadas para comparação e as processa no formato QgsVectorLayer.

        Args:
            selected_wfs (list): Lista contendo informações das bases de dados WFS selecionadas, obtidas de um arquivo JSON.
            operation_config (dict): Configurações da operação em andamento.

        Returns:
            tuple: Uma lista com os dados das camadas WFS no formato QgsVectorLayer e o dicionário atualizado de configurações.
        """
        list_selected_wfs = []

        # Cria uma lista com dados no formato QgsVectorLayer das áreas selecionadas para comparação
        for wfs in range(len(selected_wfs)):
            arq_wfs = selected_wfs[wfs]['diretorio']
            nome_wfs = selected_wfs[wfs]['nomeFantasiaCamada']
            lyr_wfs = QgsVectorLayer(arq_wfs, nome_wfs, 'ogr')
            lyr_wfs.setName(nome_wfs)
            lyr_wfs_reproj = lyr_process(lyr_wfs, operation_config, CRS_PADRAO)
            list_selected_wfs.append(lyr_wfs_reproj)

            operation_config.setdefault('aproximacao', {})[nome_wfs] = selected_wfs[wfs]['aproximacao']

        return list_selected_wfs, operation_config

    def read_selected_db(self, selected_db, operation_config):
        """
        Lê camadas selecionadas de um banco de dados PostgreSQL e as processa no formato QgsVectorLayer.

        Args:
            selected_db (list): Lista contendo informações das camadas de banco de dados selecionadas, obtidas de um arquivo JSON.
            operation_config (dict): Configurações da operação em andamento.

        Returns:
            tuple: Uma lista com os dados das camadas do banco no formato QgsVectorLayer e o dicionário atualizado de configurações.
        """
        list_selected_db = []

        # Cria uma lista com dados no formato QgsVectorLayer das áreas selecionadas para comparação
        for item_db in selected_db:
            camada = item_db['tabelasCamadas']
            nome = item_db['nomeFantasiaCamada']
            host = item_db['host']
            dbase = item_db['baseDeDados']
            port = item_db['porta']
            user = item_db['usuario']
            pwd = item_db['senha']
            
            uri = QgsDataSourceUri()
            uri.setConnection(host, port, dbase, user, pwd)
            uri.setDataSource('public', f'{camada}', 'geom')

            lyr_db = QgsVectorLayer(uri.uri(False), camada, 'postgres')
            lyr_db.setName(nome)
            lyr_db_reproj = lyr_process(lyr_db, operation_config, CRS_PADRAO)
            list_selected_db.append(lyr_db_reproj)

            operation_config.setdefault('aproximacao', {})[camada] = item_db['aproximacao']

        return list_selected_db, operation_config

    def read_required_layers(self, required_list, operation_config):
        """
        Lê as camadas obrigatórias, sejam shapefiles ou camadas de banco de dados, e as processa.

        Args:
            required_list (list): Lista contendo informações das camadas obrigatórias.
            operation_config (dict): Configurações da operação em andamento.

        Returns:
            tuple: Uma lista com as camadas obrigatórias no formato QgsVectorLayer e o dicionário atualizado de configurações.
        """
        list_required = []
        for item in required_list:
            if item['tipo'] == 'shp':
                lyr_shp, operation_config = self.read_selected_shp([item], operation_config)
                list_required.append(lyr_shp[0])
            else:
                lyr_db, operation_config = self.read_selected_db([item], operation_config)
                list_required.append(lyr_db[0])

        return list_required, operation_config
