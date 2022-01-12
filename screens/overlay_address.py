import sys
import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

from geopandas.tools import geocode

from ..settings.env_tools import EnvTools

class OverlayAddress (QtWidgets.QDialog):

    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

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

        if(self.txt_logradouro.text() != '' and self.txt_numero.text() != '' and self.txt_cidade.text() != '' and self.txt_uf.text() != ''):
            try:
                address = (self.txt_logradouro.text() + ", " + self.txt_numero.text() + ", " + self.txt_cidade.text()
                + ", " + self.txt_uf.text() + ", Brasil")

                print(self.env_tools.get_current_geocoding_server())

                print("Endereço: ", address)
                points = geocode(address, provider='nominatim', user_agent='csc_user_ht')
                # points = geocode(address, provider='google', api_key='AIzaSyD5FVX9EaxuM2ekd1t0ijtNE5BYq8D32io', user_agent='csc_user_ht', timeout=10)
                print("Points: ", points)

            except():
                self.iface.messageBar().pushMessage("Error", "Endereço não encontrado ou serviço indisponível no momento.", level=1)

        # self.hide()
        # self.continue_window.emit()