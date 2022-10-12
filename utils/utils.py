import geopandas as gpd

from ..settings.json_tools import JsonTools

class Utils():
    def __init__(self):
        """
        Método de inicialização da classe.
        """

    def add_input_approximation_geographic(self, input, approximation):
        """
        Adição de buffer de proximidade nos dados de input (EPSG's geográficos).

        @keyword input: Camada de input inserida pelo usuário.
        @keyword approximation: Buffer de aproximação inserido pelo usuário.
        @return input: Camada de input contendo o buffer de aproximação inserido.
        """

        # Transforma metros em graus
        approximation = approximation / 111319.5432

        input['geometry'] = input['geometry'].buffer(approximation)
        return input

    def add_layers_approximation_geographic(self, layer, approximation, operation_config):
        """
        Adição de buffer de proximidade nos dados de input (EPSG's geográficos).

        @keyword input: Camada de input inserida pelo usuário.
        @keyword approximation: Buffer de aproximação inserido pelo usuário.
        @return input: Camada de input contendo o buffer de aproximação inserido.
        """

        # Transforma metros em graus
        approximation = approximation / 111319.5432

        input['geometry'] = input['geometry'].buffer(approximation)
        return input

    def add_input_approximation_projected(self, input, approximation):
        """
        Adição de buffer de proximidade nos dados de input (EPSG's projetados).

        @keyword input: Camada de input inserida pelo usuário.
        @keyword approximation: Buffer de aproximação inserido pelo usuário.
        @return input: Camada de input contendo o buffer de aproximação inserido.
        """
        input['geometry'] = input['geometry'].buffer(approximation)
        return input

    def add_input_scale(self, input):
        """
        Adiciona uma escala de 50 em x e y para o dado de input.

        @keyword input: Camada de input inserida pelo usuário.
        """
        scaled_input = input.copy()

        scaled_input.geometry = scaled_input.geometry.buffer(0.05)
        return scaled_input

    def get_active_basemap(self):
        json_tools = JsonTools()
        json_basemap = json_tools.get_config_basemap()

        basemap = None
        for data in json_basemap:
            if data[2] == "True":
                basemap = data

        return basemap[0], basemap[1]