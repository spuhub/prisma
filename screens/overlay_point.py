import sys
import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

from geopandas.tools import geocode
import geopandas as gpd

from qgis.utils import iface

from ..settings.env_tools import EnvTools

class OverlayPoint (QtWidgets.QDialog):
    """
    Classe que manipula a tela de teste de sobreposição utilizando um ponto (lat e long) ou endereço inserido.
    """
    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal(dict)

    def __init__(self):
        """Método construtor da classe."""
        super(OverlayPoint, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'overlay_point.ui'), self)

        self.btn_voltar.clicked.connect(self.back)
        self.btn_continuar.clicked.connect(self.next)

        # Objeto que manipula dados armazenados na cache do QGis
        self.env_tools = EnvTools()

    def back(self):
        """
        Retorna para tela anterior.
        """
        self.hide()
        self.back_window.emit()


    def next(self):
        """
        Faz o controle dos dados de input inseridos pelo usuário e monta a operação que será feita.
        dentro da variável data, que por sua vez possui uma estrutura de dicinário
        """
        input = []

        if self.txt_logradouro.text() != '' and self.txt_numero.text() != '' and self.txt_bairro.text() != '' and self.txt_cidade.text() != '' and self.txt_uf.text() != '':
            input = self.handle_address()

            data = {"operation": "coordinate", "input": input}

            # Caso usuário tenha inserido área de aproximação
            if self.txt_aproximacao.text() != '' and float(self.txt_aproximacao.text()) > 0:
                data['aproximacao'] = float(self.txt_aproximacao.text())

            self.hide()
            self.continue_window.emit(data)

        elif self.txt_lat.text() != '' and self.txt_lon.text() != '' and self.txt_epsg.text() != '':
            if self.txt_epsg.text().isnumeric():
                input = self.handle_coordinate()

                data = {"operation": "coordinate", "input": input}

                # Caso usuário tenha inserido área de aproximação
                if self.txt_aproximacao.text() != '' and float(self.txt_aproximacao.text()) > 0:
                    data['aproximacao'] = float(self.txt_aproximacao.text())

                self.hide()
                self.continue_window.emit(data)
            else:
                iface.messageBar().pushMessage("Warning:",
                                               "O campo Sistema de coordenadas deve ser preenchido somente com números.",
                                               level=1)
        else:
            iface.messageBar().pushMessage("Warning:",
                                           "Preencher todos os campos para pesquisa.",
                                           level=1)

    def handle_address(self):
        """
            Manipulação dos dados de endereço; Extração de pontos através de endereço.

            @return dataframe: Estrutura de geodataframe contendo o endereço e os pontos que representam aquele endereço.
        """
        try:
            address = (self.txt_logradouro.text() + ", " + self.txt_numero.text() + ", " + self.txt_cidade.text()
                       + ", " + self.txt_uf.text() + ", Brasil")

            # current_geocoding = self.env_tools.get_current_geocoding_server()
            current_geocoding = ["Nominatim (OpenStreetMap)", 1]
            # key = self.get_key(current_geocoding[0])
            key = ""

            points = self.get_points(address, current_geocoding, key)
            dataframe = self.address_to_geodataframe(points)

            # points = geocode(address, provider='google', api_key='AIzaSyD5FVX9EaxuM2ekd1t0ijtNE5BYq8D32io', user_agent='csc_user_ht', timeout=10)
            return dataframe

        except():
            iface.messageBar().pushMessage("Error", "Endereço não encontrado ou serviço indisponível no momento.",
                                                level=1)

    def handle_coordinate(self):
        """
        Processa os dados passados, retornando os pontos em estrutura de geodataframe.

        @return dataframe: Geodataframe conténdo os pontos passados pelo usuário.
        """
        lat = self.txt_lat.text().replace(',', '.')
        lon = self.txt_lon.text().replace(',', '.')

        # Cria o objeto de ponto através da longitude e latitude inseridas pelo usuário
        points = gpd.points_from_xy([lon], [lat])
        epsg_coordinate = self.txt_epsg.text()

        dataframe = self.coordinate_to_geodataframe(points, epsg_coordinate)
        return dataframe

    def get_points(self, address, current_geocoding, key):
        """
        Serviço de geocodificação, funciona com Nominatim e Google maps

        @keyword address: Endereço inserido pelo usuário.
        @keyword current_geocoding: Serviço de geocodificação selecionado pelo usuário.
        @keyword key: Caso necessária, chave que será utilizada para fazer o uso do serviço de geocodificação.
        @return points: Pontos extraídos pelo serviço de geocodificação.
        """

        points = None
        if current_geocoding[0] == "Google":
            print("Google")
            points = geocode(address, provider='google', api_key=key, user_agent='csc_user_ht', timeout=10)

        elif current_geocoding[0] == "Nominatim (OpenStreetMap)":
            print("Nominatim (OpenStreetMap)")
            points = geocode(address, provider='nominatim', user_agent='csc_user_ht', timeout=10)

        return points

    def address_to_geodataframe(self, points):
        """
        Compila os dados inseridos e o ponto encontrado na estrutura de geodataframe.

        @keyword points: Pontos obtidos através do serviço de geocodificação.
        @return dataframe: Estrutura de geodataframe contendo o endereço e os pontos que representam aquele endereço.
        """
        data = {
            'logradouro': self.txt_logradouro.text(),
            'numero': self.txt_numero.text(),
            'cidade': self.txt_cidade.text(),
            'bairro': self.txt_bairro.text(),
            'uf': self.txt_uf.text(),
            'cep': self.txt_cep.text(),
            'geometry': points['geometry'][0]
        }

        dataframe = gpd.GeoDataFrame([data], geometry='geometry', crs=4674)
        dataframe = dataframe.to_crs(4326)
        dataframe.set_crs(4326, allow_override=True)

        return dataframe

    def coordinate_to_geodataframe(self, points, epsg):
        """
        Adatpa os pontos para estrutura de geodataframe.

        @keyword points: Ponto (lat e long) passado pelo usuário.
        @return dataframe: Estrutura de geodataframe contendo os pontos passados pelo usuário.
        """
        epsg = "EPSG:" + epsg

        dataframe = gpd.GeoDataFrame([], geometry=points, crs=epsg)
        dataframe = dataframe.to_crs(4326)
        dataframe.set_crs(4326, allow_override=True)

        return dataframe