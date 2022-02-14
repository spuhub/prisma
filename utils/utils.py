import geopandas as gpd

class Utils():
    def __init__(self):
        pass

    # Adição de buffer de proximidade nos dados de input (EPSG's geográficos)
    def add_input_approximation_geographic(self, input, approximation):
        # Transforma metros em graus
        approximation = approximation / 111319.5432

        input['geometry'] = input['geometry'].buffer(approximation)
        return input

    # Adição de buffer de proximidade nos dados de input (EPSG's projetados)
    def add_input_approximation_projected(self, input, approximation):
        input['geometry'] = input['geometry'].buffer(approximation)
        return input

    # Adiciona uma escala de 15 em x e y para o dado de input
    def add_input_scale(self, input):
        scaled_input = input.copy()

        scaled_input.geometry = scaled_input.scale(50, 50)
        return scaled_input
