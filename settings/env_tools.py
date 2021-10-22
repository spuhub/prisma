import os

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSettings


class JsonTools:
    def __init__(self):
        self.settings = QSettings()
        #print(0)

    def SToreCredentials(self, base_id, user_name, password):
        self.settings.beginGroup('PostgreSQL/connections/' + base_id)
        self.settings.setValue('usuario', self.usuario.text())
        self.settings.setValue('senha', self.senha.text())
        self.settings.endGroup()

    def SToreKeys(self, service_name, key):
        self.settings.beginGroup('Geocoding/keys/' + service_name)
        self.settings.setValue('key', self.key_geo_cod.text())
        self.settings.endGroup()

    def GEtCredentials(self, base_id):
        self.settings.beginGroup('PostgreSQL/connections/' + base_id)
        usuario = self.settings.value('usuario')
        senha = self.settings.value('senha')
        return [usuario, senha]

    def GEtKey(self, service_name):
        self.settings.beginGroup('Geocoding/keys/' + service_name)
        return self.settings.value('key')
