import os

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSettings


class EnvTools:
    def __init__(self):
        self.settings = QSettings()
        #print(0)

    def store_credentials(self, base_id, user_name, password):
        self.settings.beginGroup('prisma/databases/' + base_id)
        self.settings.setValue('usuario', user_name)
        self.settings.setValue('senha', password)
        self.settings.endGroup()
        #self.settings.remove("")
        #print(self.settings.allKeys())

    def edit_credentials(self, base_id,new_user_name, new_password):
        self.settings.setValue('prisma/databases/' +base_id+ '/usuario', new_user_name)
        self.settings.setValue('prisma/databases/' +base_id+ '/senha', new_password)
        #self.settings.remove("")
        #print(self.settings.allKeys())


        #usuario = self.settings.value('usuario')
        #senha = self.settings.value('senha')
        #self.settings.endGroup()
        #print(usuario, senha)
        #self.settings.remove("")
        #print(self.settings.allKeys())

    def store_keys(self, service_name, key):
        self.settings.beginGroup('Geocoding/keys/' + service_name)
        self.settings.setValue('key', key)
        self.settings.endGroup()

    def store_current_geocoding_server(self, id_server):
        self.settings.beginGroup('Geocoding/currentServer')
        self.settings.setValue('current', id_server)
        self.settings.endGroup()

    def get_current_geocoding_server(self):
        id_current = self.settings.value('Geocoding/currentServer/current')
        return id_current

    def get_credentials(self, base_id):
        #self.settings.beginGroup('PostgreSQL/databases/' + base_id)
        usuario = self.settings.value('prisma/databases/' + base_id + '/usuario')
        senha = self.settings.value('prisma/databases/' + base_id + '/senha')
        return [usuario, senha]

    def get_key(self, service_name):
        self.settings.beginGroup('Geocoding/keys/' + service_name)
        return self.settings.value('key')

    def store_report_hearder(self, hearder_List):
        self.settings.beginGroup('prisma/hearderList')
        self.settings.setValue('header', hearder_List)
        self.settings.endGroup()

    def get_report_hearder(self):
        r = {}
        header = self.settings.value('prisma/hearderList/header')
        if header is None:
            return r
        else:
            return header

    def clear_repor_header(self):
        self.settings.remove('prisma/hearderList/header')



