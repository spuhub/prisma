import os

from ..settings.json_tools import JsonTools

def pre_config_json():
    """
    Realiza uma pré-configuração do arquivo json.
    Foco é pegar de forma dinâmica o diretório onde o qgis está instalado na máquina do usuário.
    """
    json_tools = JsonTools()
    json_data = json_tools.get_json()

    data: dict = {
        "default_input_polygon": f"{os.path.dirname(__file__)}/../styles/default_layers/input_A.qml",
        "default_input_line": f"{os.path.dirname(__file__)}/../styles/default_layers/input_L.qml",
        "default_input_point": f"{os.path.dirname(__file__)}/../styles/default_layers/input_P.qml",
        "buffer": f"{os.path.dirname(__file__)}/../styles/default_layers/buffer_A.qml",
        "overlay_input_polygon": f"{os.path.dirname(__file__)}/../styles/default_layers/sobreposicao_A.qml",
        "overlay_input_line": f"{os.path.dirname(__file__)}/../styles/default_layers/sobreposicao_L.qml",
        "overlay_input_point": f"{os.path.dirname(__file__)}/../styles/default_layers/sobreposicao_P.qml"
    }

    json_data.update(style_default_layers = data)
    json_tools.insert_data(json_data)