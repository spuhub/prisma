import os
from enum import Enum

class slddefaultlayers(Enum):
    POLYGON_SLD_INPUT = "/styles/default_layers/input_A.sld"
    LINE_SLD_INPUT = "/styles/default_layers/input_L.sld"
    POINT_SLD_INPUT = "/styles/default_layers/input_P.sld"
    BUFFER_SLD = "/styles/default_layers/buffer_A.sld"
    POLYGON_SLD_OVERLAY = "/styles/default_layers/sobreposicao_A.sld"
    LINE_SLD_OVERLAY = "/styles/default_layers/sobreposicao_L.sld"
    POINT_SLD_OVERLAY = "/styles/default_layers/sobreposicao_P.sld"
    VERTICES_LAYER = "/styles/default_layers/Estilo_Vertice_P.qml"
    QUOTAS_LAYER = "/styles/default_layers/Estilo_Linhas_de_Cota_L.qml"

    def get_path(self):
        get_root = os.path.dirname(__file__).split("prisma")[0] + "prisma"

        string_path = get_root + self.value
        formated_path = os.path.normpath(string_path)
        
        return formated_path