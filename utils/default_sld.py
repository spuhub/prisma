import os
from enum import Enum

class slddefaultlayers(Enum):
    POLYGON_SLD_INPUT = f"{os.path.dirname(__file__)}/../styles/default_layers/input_A.sld"
    LINE_SLD_INPUT = f"{os.path.dirname(__file__)}/../styles/default_layers/input_L.sld"
    POINT_SLD_INPUT = f"{os.path.dirname(__file__)}/../styles/default_layers/input_P.sld"
    BUFFER_SLD = f"{os.path.dirname(__file__)}/../styles/default_layers/buffer_A.sld"
    POLYGON_SLD_OVERLAY = f"{os.path.dirname(__file__)}/../styles/default_layers/sobreposicao_A.sld"
    LINE_SLD_OVERLAY = f"{os.path.dirname(__file__)}/../styles/default_layers/sobreposicao_L.sld"
    POINT_SLD_OVERLAY = f"{os.path.dirname(__file__)}/../styles/default_layers/sobreposicao_P.sld"