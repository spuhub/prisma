import os

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSettings


class EnvTools:
    """
    Classe repsonsavel por manipular informações salva na cache do QGIS
    """
    def __init__(self):
        self.settings = QSettings()
        #print(0)

    def store_credentials(self, base_id, user_name, password):
        """
        Armazena as credenciais login e senha para acessar uma base dados postgresql
        @param base_id: Id da base presenta no Json de configuração
        @param user_name: User name da base de dados.
        @param password: Senha da Base de dados
        @return: void
        """

        self.settings.beginGroup('prisma/databases/' + base_id)
        self.settings.setValue('usuario', user_name)
        self.settings.setValue('senha', password)
        self.settings.endGroup()

    def edit_credentials(self, base_id,new_user_name, new_password):
        """
        Modifica as credeciais de uma base de dados do postgresql
        @param base_id: Id da base presenta no Json de configuração
        @param new_user_name: Novo user name da base de dados
        @param new_password: Nova senha da Base de dados
        @return:
        """
        self.settings.setValue('prisma/databases/' +base_id+ '/usuario', new_user_name)
        self.settings.setValue('prisma/databases/' +base_id+ '/senha', new_password)

    def store_keys(self, service_id, key):
        """
        Armazena a chave do serviço de geocodificação (Ex.: Google)
        @param service_id: Id do Serviço
        @param key: chave do serviço
        @return:
        """
        self.settings.beginGroup('Geocoding/keys/' + service_id)
        self.settings.setValue('key', key)
        self.settings.endGroup()

    def store_current_geocoding_server(self, server_inf):
        """
        Armazena serviço de geocodificação atualmente selecionado nas configurações
        @param server_inf: Id do Serviço
        @return: void
        """
        self.settings.beginGroup('Geocoding/currentServer')
        self.settings.setValue('current', server_inf)
        self.settings.endGroup()

    def get_current_geocoding_server(self):
        """
        Retorna serviço de geocodificação atualmente selecionado nas configurações
        @return: Id do Serviço
        """
        server_inf = self.settings.value('Geocoding/currentServer/current')
        return server_inf

    def get_credentials(self, base_id):

        """
        Retorna as as credeciais de uma base de dados do postgresql
        @param base_id: Id da base presente no Json de configuração
        @return:
        """

        usuario = self.settings.value('prisma/databases/' + base_id + '/usuario')
        senha = self.settings.value('prisma/databases/' + base_id + '/senha')
        print("USER:", base_id, usuario, senha)
        return [usuario, senha]

    def get_key(self, service_id):

        """
        Retorna a chave de um serviço de Geocodificação
        @param service_id: Id do serviço do Geocodificação
        @return: chave do serviço de Geocodificação
        """
        self.settings.beginGroup('Geocoding/keys/' + service_id)
        return self.settings.value('key')

    def store_report_hearder(self, hearder_List):

        """
        Armazena na cache as iformações de cabeçalho do relatório
        @param hearder_List: Json com as informações do cabeçalho
        @return:
        """
        self.settings.beginGroup('prisma/hearderList')
        self.settings.setValue('header', hearder_List)
        self.settings.endGroup()

    def get_report_hearder(self):
        """
        Retorna cache as infnormações de cabeçalho do relatório
        @return: Json com as informações de cabeçalho
        """
        r = {}
        header = self.settings.value('prisma/hearderList/header')
        if header is None:
            return r
        else:
            return header

    def clear_repor_header(self):
        """
        Apaga da cache as informações de cabeçalho dos relatorios
        @return:
        """
        self.settings.remove('prisma/hearderList/header')



