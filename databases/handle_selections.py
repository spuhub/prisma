from qgis.core import QgsVectorLayer, QgsDataSourceUri
from ..utils.lyr_utils import *

class HandleSelections():
    """
    Classe para leitura de objetos selecionados para comparação.
    """
    def __init__(self):
        """
        Método de inicialização da classe.

        """

    def read_selected_shp(self, selected_shapefiles):
        """
        Método que lê arquivos shapefiles selecionados para comparação.

        @keyword selected_shapefiles: Vetor contendo informações das bases de dados selecionadas para comparação, essas informações são obtidas do arquivo JSON.
        @return input: lista contendo os shapefiles selecionados para comparação.
        """
        list_selected_shp = []

        # Cria uma lista com dados no formato QgsVectorLayer das áreas selecionadas para comparação
        for shp in range(len(selected_shapefiles)):
            arq_shp = selected_shapefiles[shp]['diretorioLocal']
            nome_shp = selected_shapefiles[shp]['nome']
            lyr_shp = QgsVectorLayer(arq_shp, nome_shp, 'ogr')
            lyr_shp_reproj = lyr_process(lyr_shp, 4326)
            lyr_shp_reproj.setName(nome_shp)
            list_selected_shp.append(lyr_shp_reproj)

        return list_selected_shp

    def read_selected_wfs(self, selected_wfs):
        """
        Método que lê arquivos wfs selecionados para comparação.

        @keyword selected_wfs: Vetor contendo informações das bases de dados selecionadas para comparação, essas informações são obtidas do arquivo JSON.
        @return input: lista contendo os dados dos WFS selecionados para comparação.
        """
        list_selected_wfs = []

        # Cria uma lista com dados no formato QgsVectorLayer das áreas selecionadas para comparação
        for wfs in range(len(selected_wfs)):
            arq_wfs = selected_wfs[wfs]['diretorio']
            nome_wfs = selected_wfs[wfs]['nomeFantasiaTabelasCamadas']
            lyr_wfs = QgsVectorLayer(arq_wfs, nome_wfs, 'ogr')
            lyr_wfs_reproj = lyr_process(lyr_wfs, 4326)
            lyr_wfs_reproj.setName(nome_wfs)
            list_selected_wfs.append(lyr_wfs_reproj)

        return list_selected_wfs

    def read_selected_db(self, selected_db):
        """
        Método que lê camadas do postgresql selecionados para comparação.

        @keyword selected_db: Vetor contendo informações das bases de dados selecionadas para comparação, essas informações são obtidas do arquivo JSON.
        @return input: lista contendo os dados do banco de dados selecionados para comparação.
        """
        list_selected_db = []

        # Cria uma lista com dados no formato QgsVectorLayer das áreas selecionadas para comparação
        for item_db in selected_db:
            camada = item_db['tabelasCamadas'][0]
            host = item_db['host']
            dbase = item_db['baseDeDados']
            port = item_db['porta']
            user = item_db['usuario']
            pwd = item_db['senha']
            
            uri = QgsDataSourceUri()
            uri.setConnection(host, port, dbase, user, pwd)
            uri.setDataSource('public', f'{camada}', 'geom')

            lyr_db = QgsVectorLayer(uri.uri(False), camada, 'postgres')
            lyr_db_reproj = lyr_process(lyr_db, 4326)
            lyr_db_reproj.setName(camada)
            list_selected_db.append(lyr_db_reproj)

        return list_selected_db

    def read_required_layers(self, required_list):
        list_required = []
        for item in required_list:
            if item['tipo'] == 'shp':
                lyr_shp = self.read_selected_shp([item])[0]
        
                list_required.append(lyr_shp)
            else:
                lyr_db = self.read_selected_db([item])[0]
                list_required.append(lyr_db)

        return list_required