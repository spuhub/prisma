import geopandas as gpd

class ShpHandle():
    def __init__(self):
        pass

    # Método que lê arquivo shapefile de input
    def read_shp_input(self, input_dir):
        input = gpd.read_file(input_dir)
        input = input.to_crs(epsg='4674') # tranforma dados para sistema de coordenadas de referência adotados como padrão no projeto (EPSG:4674)

        return input

    # Método que lê arquivos shapefiles selecionados para comparação
    def read_selected_shp(self, selected_shapefiles):
        gdf_selected_shp = []

        # Cria uma lista com dados no formato geopandas das áreas selecionadas para comparação
        for shp in range(len(selected_shapefiles)):
            gdf_selected_shp.append(gpd.read_file(selected_shapefiles[shp]['diretorioLocal']))
            gdf_selected_shp[shp] = gdf_selected_shp[shp].to_crs(epsg='4674') # tranforma dados para sistema de coordenadas de referência adotados como padrão no projeto (EPSG:4674)

        return gdf_selected_shp

    # Adição de buffer de proximidade nos dados de input
    def add_input_approximation(self, input, approximation):
        # Transforma metros em graus
        approximation = approximation / 111319.5432

        input_approximation = input.copy()
        input_approximation['geometry'] = input['geometry'].buffer(approximation)
        return input_approximation
