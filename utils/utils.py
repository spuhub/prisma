import geopandas as gpd

class Utils():
    def __init__(self):
        pass

    # Adição de buffer de proximidade nos dados de input (EPSG's geográficos)
    def add_input_approximation_geographic(self, input, approximation):
        # Transforma metros em graus
        approximation = approximation / 111319.5432

        input_approximation = input.copy()
        input_approximation['geometry'] = input['geometry'].buffer(approximation)
        return input_approximation

    # Adição de buffer de proximidade nos dados de input (EPSG's projetados)
    def add_input_approximation_projected(self, input, approximation):
        input_approximation = input.copy()
        input_approximation['geometry'] = input['geometry'].buffer(approximation)
        return input_approximation