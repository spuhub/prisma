import os

from PyQt5.QtCore import QSettings

class EnvTools:
    """
    Classe responsável por gerenciar informações armazenadas na cache do QGIS.

    Utilizada para manipular credenciais de banco de dados, serviços de geocodificação, 
    cabeçalhos de relatórios e caminho do JSON de configuração.

    Atributos:
        settings (QSettings): Gerencia a persistência de dados na cache do QGIS.
    """
    def __init__(self):
        self.settings = QSettings()

    def store_credentials(self, base_id, user_name, password):
        """
        Armazena as credenciais de login e senha para uma base de dados PostgreSQL.

        Args:
            base_id (str): ID da base presente no JSON de configuração.
            user_name (str): Nome de usuário da base de dados.
            password (str): Senha da base de dados.
        """
        s = QSettings()
        path = 'prisma/databases/' + base_id
        s.setValue(path + '/usuario', user_name)
        s.setValue(path + '/senha', password)

    def edit_credentials(self, base_id,new_user_name, new_password):
        """
        Edita as credenciais armazenadas de uma base de dados PostgreSQL.

        Args:
            base_id (str): ID da base presente no JSON de configuração.
            new_user_name (str): Novo nome de usuário.
            new_password (str): Nova senha.
        """
        s = QSettings()
        s.setValue('prisma/databases/' + base_id + '/usuario', new_user_name)
        s.setValue('prisma/databases/' + base_id + '/senha', new_password)

    def store_keys(self, service_id, key):
        """
        Armazena a chave de um serviço de geocodificação (por exemplo, Google).

        Args:
            service_id (str): ID do serviço de geocodificação.
            key (str): Chave do serviço.
        """
        s = QSettings()
        s.setValue('prisma/geocoding/keys/' + str(service_id), key)

    def store_current_geocoding_server(self, server_inf):
        """
        Armazena serviço de geocodificação atualmente selecionado nas configurações
        @param server_inf: Id do Serviço
        @return: void
        """
        s = QSettings()
        s.setValue('prisma/geocoding/current', server_inf)

    def get_current_geocoding_server(self):
        """
        Retorna serviço de geocodificação atualmente selecionado nas configurações
        @return: Id do Serviço
        """
        s = QSettings()
        server_inf = s.value('prisma/geocoding/current', 0)
        return server_inf

    def get_credentials(self, base_id):
        """
        Retorna as credenciais de uma base de dados PostgreSQL.

        Args:
            base_id (str): ID da base presente no JSON de configuração.

        Returns:
            list: Lista contendo [usuario, senha].
        """
        s = QSettings()
        usuario = s.value('prisma/databases/' + base_id + '/usuario')
        senha = s.value('prisma/databases/' + base_id + '/senha')
        return [usuario, senha]

    def get_key(self, service_id):
        """
        Retorna a chave armazenada para um serviço de geocodificação.

        Args:
            service_id (str): ID do serviço de geocodificação.

        Returns:
            str: Chave do serviço de geocodificação.
        """
        s = QSettings()
        key = s.value('prisma/geocoding/keys/' + str(service_id),"")
        return key

    def store_report_hearder(self, hearder_List):
        """
        Armazena as informações de cabeçalho do relatório na cache.

        Args:
            hearder_list (dict): JSON com as informações do cabeçalho.
        """
        self.settings.beginGroup('prisma/hearderList')
        self.settings.setValue('header', hearder_List)
        self.settings.endGroup()

    def get_report_hearder(self):
        """
        Retorna as informações de cabeçalho do relatório armazenadas na cache.

        Returns:
            dict: JSON com as informações do cabeçalho.
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

    def store_path_json(self, path):
        """
        Armazena o caminho do arquivo JSON de configuração na cache.

        Args:
            path (str): Caminho do arquivo JSON.
        """
        s = QSettings()
        s.setValue('prisma/json', path)

    def get_path_json(self):
        """
        Retorna o caminho de configuração
        """
        try:
            s = QSettings()
            server_inf = s.value('prisma/json')
            if server_inf is None:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                return base_dir + "/settings/config_Json/dbtabases.json"
            else:
                return server_inf

        except Exception as erro:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            return base_dir + "/settings/config_Json/dbtabases.json"







