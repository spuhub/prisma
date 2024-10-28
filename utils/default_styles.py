import os
from enum import Enum

class default_styles(Enum):
    POLYGON_STYLE_INPUT = "/styles/default_layers/input_A.qml"
    LINE_STYLE_INPUT = "/styles/default_layers/input_L.qml"
    POINT_STYLE_INPUT = "/styles/default_layers/input_P.qml"
    BUFFER_STYLE = "/styles/default_layers/buffer_A.qml"
    POLYGON_STYLE_OVERLAY = "/styles/default_layers/sobreposicao_A.qml"
    LINE_STYLE_OVERLAY = "/styles/default_layers/sobreposicao_L.qml"
    POINT_STYLE_OVERLAY = "/styles/default_layers/sobreposicao_P.qml"
    VERTICES_LAYER = "/styles/default_layers/Estilo_Vertice_P.qml"
    QUOTAS_LAYER = "/styles/default_layers/Estilo_Linhas_de_Cota_L.qml"

    def get_path(self):
        get_root = os.path.dirname(__file__).split("prisma")[0] + "prisma"

        string_path = get_root + self.value
        formated_path = os.path.normpath(string_path)
        
        return formated_path