import os
from enum import Enum

class slddefaultlayers(Enum):
    POLYGON_SLD_INPUT = f"{os.path.dirname(__file__)}/../styles/3_2_2_Trecho_Terreno_Marinha_A.sld"
    LINE_SLD_INPUT = f"{os.path.dirname(__file__)}/../styles/1_6_5_Trecho_Duto_L.sld"
    POINT_SLD_INPUT = f"{os.path.dirname(__file__)}/../styles/1_6_1_Estrut_Apoio_Transporte_P.sld"
    BUFFER_SLD = f"{os.path.dirname(__file__)}/../styles/1_2_3_Massa_Dagua_A.sld"
    POLYGON_SLD_OVERLAY = f"{os.path.dirname(__file__)}/../styles/1_5_6_Elemento_Fisiografico_Natural_A.sld"
    LINE_SLD_OVERLAY = f"{os.path.dirname(__file__)}/../styles/1_5_8_Curva_Nivel_L.sld"
    POINT_SLD_OVERLAY = f"{os.path.dirname(__file__)}/../styles/1_6_2_Estacao_Ferroviario_P.sld"