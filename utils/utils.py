from ..settings.json_tools import JsonTools

class Utils():
    def __init__(self):
        """
        Método de inicialização da classe.
        """

    def add_input_scale(self, input):
        """
        Adiciona um buffer de escala de 0.05 (ou 50 unidades) nas coordenadas X e Y da geometria do dado de entrada.

        Args:
            input (QgsFeature): Feição de entrada inserida pelo usuário.

        Returns:
            QgsFeature: Feição de entrada com a geometria escalada.
        """
        scaled_input = input.copy()

        scaled_input.geometry = scaled_input.geometry.buffer(0.05)
        return scaled_input

    def get_active_basemap(self):
        """
        Retorna o basemap ativo configurado no sistema.

        Returns:
            tuple: Um par de valores (str, str) contendo o identificador e o caminho do basemap ativo.

        Raises:
            Exception: Caso nenhum basemap esteja marcado como ativo.
        """
        json_tools = JsonTools()
        json_basemap = json_tools.get_config_basemap()

        basemap = None
        for data in json_basemap:
            if data[2] == "True":
                basemap = data

        return basemap[0], basemap[1]

    