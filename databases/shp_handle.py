import geopandas as gpd

class ShpHandle():
    """
    Classe para leitura e manipulação de arquivos shapefile.
    """
    def __init__(self):
        """
        Método de inicialização da classe.
        """
        pass

    def read_shp_input(self, input_dir):
        """
        Método que lê arquivo shapefile de input.

        @keyword input_dir: Diretório onde o arquivo shapefile de input está armazenado.
        @return input: Geodataframe contendo os dados do shapefile de input.
        """
        input = gpd.read_file(input_dir)
        input = input.to_crs(4326)
        input.set_crs(allow_override=True, crs=4326) # tranforma dados para sistema de coordenadas de referência adotados como padrão no projeto (EPSG:4674)

        return input

    def read_selected_shp(self, selected_shapefiles):
        """
        Método que lê arquivos shapefiles selecionados para comparação.

        @keyword selected_shapefiles: Vetor contendo informações das bases de dados selecionadas para comparação, essas informações são obtidas do arquivo JSON.
        @return input: Geodataframe contendo os dados do shapefile de input.
        """
        gdf_selected_shp = []

        # Cria uma lista com dados no formato geopandas das áreas selecionadas para comparação
        for shp in range(len(selected_shapefiles)):
            gdf_selected_shp.append(gpd.read_file(selected_shapefiles[shp]['diretorioLocal']))
            gdf_selected_shp[shp] = gdf_selected_shp[shp].to_crs(4326)
            gdf_selected_shp[shp].set_crs(allow_override=True, crs=4326) # tranforma dados para sistema de coordenadas de referência adotados como padrão no projeto (EPSG:4674)

        return gdf_selected_shp