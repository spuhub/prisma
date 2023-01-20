from ..databases.db_connection import DbConnection
from ..databases.shp_handle import ShpHandle
from .utils import Utils

import geopandas as gpd
from shapely.wkt import loads

class DataProcessing():
    def __init__(self):
        """Método construtor da classe."""
        self.shp_handle = ShpHandle()
        self.utils = Utils()

    def data_preprocessing(self, operation_config):
        # Leitura do shapefile de input
        input = operation_config['input']
        input = input.to_crs(4326)
        input_standard = input.copy()

        # Cálculo do buffer de proximidade
        if 'aproximacao' in operation_config:
            input = self.utils.add_input_approximation_geographic(input, operation_config['aproximacao'])

        # Leitura de shapefiles de comparação
        gdf_selected_shp = self.shp_handle.read_selected_shp(operation_config['shp'])
        gdf_selected_wfs = self.shp_handle.read_selected_wfs(operation_config['wfs'])

        scaled_input = self.utils.add_input_scale(input)
        # Aquisição dos dados vindos de banco de dados
        gdf_selected_db = self.get_db_layers(scaled_input, operation_config['pg'])
        # Cria Geodataframe selecionados como bases de dados obrigatórios
        gdf_selected_shp, gdf_selected_db, operation_config = self.get_required_layers(scaled_input, operation_config, gdf_selected_shp, gdf_selected_db)
        gdf_selected_shp_standard = gdf_selected_shp.copy()

        for index, layer in enumerate(gdf_selected_shp):
            if 'aproximacao' in operation_config['shp'][index] and operation_config['shp'][index]['aproximacao'][0] > 0:
                gdf_selected_shp[index] = self.utils.add_input_approximation_geographic(layer, operation_config['shp'][index]['aproximacao'][0])

        # Elimina feições de comparação distantes das feições de input
        gdf_selected_shp = self.eliminate_distant_features_shp(scaled_input, gdf_selected_shp)
        gdf_selected_wfs = self.eliminate_invalid_geometrys(gdf_selected_wfs)

        for index, layer in enumerate(gdf_selected_wfs):
            if 'aproximacao' in operation_config['wfs'][index] and operation_config['wfs'][index]['aproximacao'] > 0:
                gdf_selected_wfs[index] = self.utils.add_input_approximation_geographic(layer, operation_config['wfs'][index]['aproximacao'])

        # Elimina feições de comparação distantes das feições de input
        gdf_selected_wfs = self.eliminate_distant_features_shp(scaled_input, gdf_selected_wfs)

        return input, input_standard, gdf_selected_shp, gdf_selected_shp_standard, gdf_selected_wfs, gdf_selected_db, operation_config

    def eliminate_invalid_geometrys(self, gdf_selected_wfs):
        '''
        Elimina geometrias inválidas vindas da base de dados WFS
        :param gdf_selected_wfs:
        :return:
        '''
        for i in range(len(gdf_selected_wfs)):
            gdf_selected_wfs[i] = gdf_selected_wfs[i].to_crs(4326)
            for indexArea, rowArea in gdf_selected_wfs[i].iterrows():
                if 'geometry' not in rowArea:
                    gdf_selected_wfs[i].drop(indexArea, inplace=True)
                    continue

                if rowArea['geometry'] == None:
                    gdf_selected_wfs[i].drop(indexArea, inplace=True)
                    continue

                if not rowArea['geometry'].is_valid:
                    gdf_selected_wfs[i].drop(indexArea, inplace=True)

        return gdf_selected_wfs

    def get_db_layers(self, scaled_input, operation_config):
        """
        Carrega as bases de dados selecionadas para conparação, vindas de banco de dados
        """
        # Configuração acesso banco de dados Postgis junto das camadas que serão utilizadas
        databases = []
        for db in operation_config:
            if 'aproximacao' in db:
                databases.append(
                    {'connection': DbConnection(db['host'], db['porta'], db['baseDeDados'], db['usuario'], db['senha']),
                     'layers': db['tabelasCamadas'], 'buffer': db['aproximacao']})
            else:
                databases.append(
                    {'connection': DbConnection(db['host'], db['porta'], db['baseDeDados'], db['usuario'], db['senha']),
                     'layers': db['tabelasCamadas'], 'buffer': None})

        # Cria lista com as bases de dados dos bancos de dados que foram selecionadas para comparação
        gdf_selected_db = []
        for index_db, database in enumerate(databases):
            layers_db = []
            for index, layer in enumerate(database['layers']):
                approximation = None
                if database['buffer'] != None:
                    approximation = database['buffer'][index] / 111319.5432
                gdf, crs = database['connection'].CalculateIntersectGPD(scaled_input, layer, approximation,
                                                                        (str(scaled_input.crs)).replace('epsg:', ''))
                if len(gdf) > 0 and crs != None:
                    # gdf.crs = {'init': 'epsg:' + str(crs)}

                    layers_db.append(gpd.GeoDataFrame(gdf, crs=crs, geometry='geometry'))

            gdf_selected_db.append(layers_db)
        return gdf_selected_db

    def get_required_layers(self, scaled_input, operation_config, gdf_selected_shp, gdf_selected_db):
        for i in range(len(operation_config['required'])):
            if operation_config['required'][i]['tipo'] == 'shp':
                operation_config['shp'].append(operation_config['required'][i])
                get_shp = self.shp_handle.read_selected_shp([operation_config['required'][i]])[0]
                gdf_selected_shp.append(get_shp)
            else:
                operation_config['pg'].append(operation_config['required'][i])
                get_db = self.get_db_layers(scaled_input, [operation_config['required'][i]])[0]
                gdf_selected_db.append(get_db)

        # gdf_required = self.to_list(gdf_required)
        return gdf_selected_shp, gdf_selected_db, operation_config

    def eliminate_distant_features_shp(self, scaled_input, gdf_selected_shp):
        """Método utilizado para eliminar feições das camadas de comparação que estão distantes das feições de input.
        Serve para melhorar o desempenho para processamentos futuros, como por exemplo geração de plantas PDF e mostrar áreas no mostrador do QGIS.
        Vale ressaltar que essa função existe somente para shapefile pois, com banco de dados essa operação já acontece no lado do banco de dados

        @keyword scaled_input: Camada de input, com o acrescimo da função escala para obter, através de teste de sobreposição, áreas próximas ao input.
        @keyword gdf_selected_shp: Camadas de banco de dados selecionadas para comparação.
        @return gdf_selected_shp: Retorna as camadas shapefiles contendo somente áreas próximas à camada de input.
        """
        index = 0
        for i in range(len(gdf_selected_shp)):
            gdf_selected_shp[i]['close_input'] = False
            gdf_selected_shp[i] = gdf_selected_shp[i].to_crs(4326)
            for indexArea, rowArea in gdf_selected_shp[i].iterrows():
                for indexInput, rowInput in scaled_input.iterrows():
                    if (rowInput['geometry'].intersection(rowArea['geometry'])):
                        gdf_selected_shp[i].loc[indexArea, 'close_input'] = True
            index += 1

        for i in range(len(gdf_selected_shp)):
            # Obriga a sempre manter ao menos um registro no GeoDataFrame
            # Serve para pegar o tipo da geometria posteriormente durante as comparações
            gdf_selected_shp[i].loc[0, 'close_input'] = True
            # Exclui áreas que não foram classificadas como perto do input (sem sobreposição ao input escalado)
            gdf_selected_shp[i] = gdf_selected_shp[i].query("close_input == True")
            gdf_selected_shp[i] = gdf_selected_shp[i].drop(columns=['close_input'])

        return gdf_selected_shp

    def to_list(self, gdf):
        if isinstance(gdf, list):
            return [sub_elem for elem in gdf for sub_elem in self.to_list(elem)]
        else:
            return [gdf]
