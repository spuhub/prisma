import os

import geopandas as gpd
import requests
from owslib.wfs import WebFeatureService
from qgis.core import QgsProject, QgsVectorLayer, QgsFillSymbol, QgsLineSymbol, QgsMarkerSymbol, QgsRasterLayer, QgsCoordinateReferenceSystem

class WfsOperations:

      def get_wfs_informations(self, link_wfs):

            wfs = WebFeatureService(url=link_wfs)

            layers = list(wfs.contents)

            data_wfs = []
            for data in layers:
                  data_wfs.append([data, wfs[data].title])

            return data_wfs

      def download_wfs_layer(self, link_wfs, layer, base_name):
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

