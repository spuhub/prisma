import os

from ..settings.json_tools import JsonTools

def pre_config_json():
    """
        Realiza uma pré-configuração do arquivo json.
        Foco é pegar de forma dinâmica o diretório onde o qgis está instalado na máquina do usuário.
    """
    json_tools = JsonTools()
    json_data = get_json()

    data: dict = {
        "default_input_polygon": f"{os.path.dirname(__file__)}/../styles/3_2_2_Trecho_Terreno_Marinha_A.sld",
        "default_input_line": f"{os.path.dirname(__file__)}/../styles/1_6_5_Trecho_Duto_L.sld",
        "default_input_point": f"{os.path.dirname(__file__)}/../styles/3_2_2_Trecho_Terreno_Marinha_A.sld",
        "buffer": f"{os.path.dirname(__file__)}/../styles/1_2_3_Massa_Dagua_A.sld",
        "overlay_input_polygon": f"{os.path.dirname(__file__)}/../styles/1_2_4_Terreno_Sujeito_Inundacao_A.sld",
        "overlay_input_line": f"{os.path.dirname(__file__)}/../styles/3_3_3_Trecho_LPM_L.sld",
        "overlay_input_point": f"{os.path.dirname(__file__)}/../styles/1_6_2_Estacao_Ferroviario_P.sld"
    }

    json_data.update(sld_default_layers = data)
    json_tools.insert_data(json_data)