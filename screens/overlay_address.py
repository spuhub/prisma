import sys
import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

from geopandas.tools import geocode
import geopandas as gpd

from qgis.utils import iface

from ..settings.env_tools import EnvTools

class OverlayAddress (QtWidgets.QDialog):

    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal(dict)

    def __init__(self):
        super(OverlayAddress, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'overlay_address.ui'), self)

        self.btn_voltar.clicked.connect(self.back)
        self.btn_continuar.clicked.connect(self.next)

        self.env_tools = EnvTools()

    def back(self):
        self.hide()
        self.back_window.emit()

    def next(self):
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
        lat = self.txt_lat.text().replace(',', '.')
        lon = self.txt_lon.text().replace(',', '.')

        points = gpd.points_from_xy([lon], [lat])
        epsg_coordinate = self.txt_epsg.text()
        print(epsg_coordinate)

        dataframe = self.coordinate_to_geodataframe(points, epsg_coordinate)
        return dataframe

    def get_points(self, address, current_geocoding, key):
        points = None
        if current_geocoding[0] == "Google":
            print("Google")
            points = geocode(address, provider='google', api_key=key, user_agent='csc_user_ht', timeout=10)

        elif current_geocoding[0] == "Nominatim (OpenStreetMap)":
            print("Nominatim (OpenStreetMap)")
            points = geocode(address, provider='nominatim', user_agent='csc_user_ht', timeout=10)

        return points

    def address_to_geodataframe(self, points):
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

        epsg = "EPSG:" + epsg

        dataframe = gpd.GeoDataFrame([], geometry=points, crs=epsg)
        dataframe = dataframe.to_crs(4326)
        dataframe.set_crs(4326, allow_override=True)

        return dataframe