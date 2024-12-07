import os

import requests
from owslib.wfs import WebFeatureService

class WfsOperations:

      def get_wfs_informations(self, link_wfs):
            """
            Obtém informações das camadas disponíveis em um serviço WFS.

            Args:
                  link_wfs (str): URL do serviço WFS.

            Returns:
                  list: Lista contendo informações das camadas disponíveis no WFS. Cada item é uma lista com:
                        - Nome da camada (str)
                        - Título da camada (str)
            """

            wfs = WebFeatureService(url=link_wfs)

            layers = list(wfs.contents)

            data_wfs = []
            for data in layers:
                  data_wfs.append([data, wfs[data].title])

            return data_wfs

      def download_wfs_layer(self, link_wfs, layer, base_name):
            """
            Faz o download de uma camada específica de um serviço WFS no formato GeoJSON.

            Args:
                  link_wfs (str): URL do serviço WFS.
                  layer (str): Nome da camada a ser baixada.
                  base_name (str): Nome base para o diretório onde o arquivo será salvo.

            Returns:
                  bool: `True` se o download foi concluído com sucesso, caso contrário `False`.
            """

            params = dict(SERVICE='WFS', VERSION="1.1.0", REQUEST='GetFeature',
                              TYPENAME=layer, OUTPUTFORMAT='json')

            url = requests.Request('GET', link_wfs, params=params).prepare().url
            response = requests.get(url)

            if response.ok:
                  safe_layer_name = layer.replace(':', '_').replace('*', '_').replace('/', '_').replace('\\', '_')

                  script_dir = os.path.dirname(os.path.abspath(__file__))
                  dir_path = os.path.join(script_dir, '..', 'wfs_layers', str(base_name))

                  if not os.path.exists(dir_path):
                        try:
                              os.makedirs(dir_path)
                        except OSError as e:
                              print(f"Erro ao criar diretório: {dir_path}: {e}")
                              return False

                  file_path = os.path.join(dir_path, safe_layer_name + ".geojson")
                  with open(file_path, "wb") as file:
                        file.write(response.content)

                  return True
            return False


      def update_wfs_layer(self, link_wfs, layer, base_name):
            """
            Atualiza uma camada existente de um serviço WFS. Caso o arquivo GeoJSON já exista, ele será removido
            e substituído pela versão mais recente.

            Args:
                  link_wfs (str): URL do serviço WFS.
                  layer (str): Nome da camada a ser atualizada.
                  base_name (str): Nome base para o diretório onde o arquivo será salvo.

            Returns:
                  bool: `True` se a camada foi atualizada com sucesso, caso contrário `False`.
            """
            params = dict(SERVICE='WFS', VERSION="1.1.0", REQUEST='GetFeature',
                  TYPENAME=layer, OUTPUTFORMAT='json')

            url = requests.Request('GET', link_wfs, params=params).prepare().url
            response = requests.get(url)

            if response.ok:
                  layer = layer\
                        .replace(':', '_')\
                        .replace('*', '_')\
                        .replace('/', '_')\
                        .replace('\\', '_')

                  dir = os.path.dirname(__file__) + '/../wfs_layers/' + base_name + '/' + layer + ".geojson"

                  if os.path.isfile(dir):
                        os.remove(dir)

                  open(dir, "wb").write(response.content)
                  return True
            return False

