import sys
import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

from .config_layers import ConfigLayers
from .json_tools import JsonTools
from .env_tools import EnvTools
from PyQt5.QtWidgets import QMessageBox

from ..screens.report_generator import ReportGenerator
from ..databases.db_connection import DbConnection


class ConfigWindow(QtWidgets.QDialog):

    """Classe reposavel por manipular a janela de configuração principal"""

    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self):
        super(ConfigWindow, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'config_window.ui'), self)
        self.setings = JsonTools()
        self.credencials = EnvTools()
        self.source_databases = self.setings.get_config_database()
        self.source_shp = self.setings.get_config_shapefile()
        self.fill_combo_box_base()
        self.fill_combo_box_shp()
        self.fill_combo_box_geocoding_server()
        self.newbdID = ''
        self.newshpID = ''

        self.btn_cancelar.clicked.connect(self.back)
        self.btn_salvar.clicked.connect(self.save_settings)
        self.test_conect.clicked.connect(self.message)
        self.testar_base_carregar_camadas.clicked.connect(self.hideLayerConfBase)
        self.testar_shp_carregar_camadas.clicked.connect(self.hideLayerConfShp)
        self.combo_box_base.activated.connect(self.fill_text_fields_base)
        self.combo_box_shp.activated.connect(self.fill_text_fields_shp)
       # self.btext.clicked.connect(self.hiderheader)

    def save_bd_config_json(self):
        """
        Método responsável pegar da interface as informações configuração de base de dados do PostgreSQL e salvar no Json de configuração.
        :return: void
        """
        confg_dic = {}
        id_current_db = self.combo_box_base.currentData()
        current_config = self.search_base_pg(id_current_db)

        if current_config != confg_dic:
            confg_dic = current_config


        confg_dic["id"] = ""
        confg_dic["tipo"] = "pg"
        confg_dic["nome"] = self.nome_base.text()
        confg_dic["host"] = self.host.text()
        confg_dic["porta"] = self.porta.text()
        confg_dic["baseDeDados"] = self.base_de_dados.text()
        confg_dic["orgaoResponsavel"] = self.orgao_responsavel_base.text()
        confg_dic["periosReferencia"] = self.perios_referencia_base.text()
        confg_dic["dataAquisicao"] = self.data_aquisicao_base.text()

        if self.combo_box_base.currentData() == "0":
            if confg_dic["nome"] != "" and confg_dic["host"] != "" and confg_dic["porta"] != "" and confg_dic[
                "baseDeDados"] != "":
                id = self.setings.insert_database_pg(confg_dic)
                self.newbdID = id
                self.source_databases.append(confg_dic)
                self.combo_box_base.addItem(self.nome_base.text(), id)
                self.credencials.store_credentials(id, self.usuario.text(), self.senha.text())
                confg_dic = {}

        else:
            index = self.search_index_base_pg(id_current_db)
            print("ID_current ==", id_current_db, index)
            self.source_databases[index] = confg_dic
            self.setings.edit_database(id_current_db, confg_dic)

            self.credencials.edit_credentials(id_current_db, self.usuario.text(), self.senha.text())
            confg_dic = {}

    def save_settings(self):
        """
        Salva as configurações de PosgreSQL e ShapeFile no Json de configuração. Executa os metodos: "save_bd_config_json" e "save_shp_config_json"
        :return:
        """
        self.save_bd_config_json()
        self.save_shp_config_json()

    def save_shp_config_json(self):
        """
        Método responsável pegar da interface as informações configuração de base de dados Shapefile e salvar no Json de configuração.
        :return:
        """
        id_current_db = self.combo_box_shp.currentData()
        current_config = self.search_base_shp(id_current_db)
        confg_dic = {}

        if current_config != confg_dic:
            confg_dic = current_config

        confg_dic["id"] = ""
        confg_dic["tipo"] = "shp"
        confg_dic["nome"] = self.nome_shp.text()
        confg_dic["urlDowload"] = self.url_dowload.text()
        confg_dic["diretorioLocal"] = self.diretorioLocalshp.filePath()
        confg_dic["orgaoResponsavel"] = self.orgao_responsavel_shp.text()
        confg_dic["periosReferencia"] = self.periodo_referencia_shp.text()
        confg_dic["dataAquisicao"] = self.data_aquisicao_shp.text()

        if self.combo_box_shp.currentData() == "0":
            if confg_dic["nome"] != "" and confg_dic["urlDowload"] != "" and confg_dic["diretorioLocal"] != "":
                id = self.setings.insert_database_pg(confg_dic)
                self.newshpID = id
                print("New id", id)
                self.source_shp.append(confg_dic)
                self.combo_box_base.addItem(self.nome_shp.text(), id)
                #self.credencials.store_credentials(id, self.usuario.text(), self.senha.text())
                confg_dic = {}

        else:
            index = self.search_index_base_shp(id_current_db)
            print("ID_current ==", id_current_db, index)
            self.source_shp[index] = confg_dic
            self.setings.edit_database(id_current_db, confg_dic)

            #self.credencials.edit_credentials(id_current_db, self.usuario.text(), self.senha.text())
            confg_dic = {}

    def fill_combo_box_base(self):
        """
        Preenche o combox com bases PostgreSQl cadastradas e presentes no Json de configuração.
        :return: void
        """
        self.combo_box_base.setItemData(0, "0")
        if len(self.source_databases) > 0:
            for item in self.source_databases:
                self.combo_box_base.addItem(item["nome"], item["id"])

    def fill_combo_box_shp(self):
        """
        Preenche o combox com bases ShapeFile cadastradas e presentes no Json de configuração.
        :return:
        """
        self.combo_box_shp.setItemData(0, "0")
        if len(self.source_shp) > 0:
            for item in self.source_shp:
                self.combo_box_shp.addItem(item["nome"], item["id"])

    def search_base_pg(self, id_base):
        """
        Busca as configurações de uma base de dados PostgreSQL apartir do seu ID
        :param id_base: ID da base dados
        :return:
        """
        config = {}
        for item in self.source_databases:
            if item["id"] == id_base:
                config = item

        return config

    def search_base_shp(self, id_base):
        """
        Busca as configurações de uma base de dados Shapefile a partir do seu ID.
        :param id_base: ID da base dados
        :return:
        """
        config = {}
        for item in self.source_shp:
            if item["id"] == id_base:
                config = item

        return config

    def search_index_base_shp(self, id_base):
        """
        Busca o index as configurações de uma base de dados Shapefile no vetor de configurações "source_shp"  a partir do seu ID.
        :param id_base: ID da base dados
        :return:
        """
        idex = 0
        for item in self.source_shp:
            if item["id"] != id_base:
                idex = idex + 1

        return idex - 1

    def search_index_base_pg(self, id_base):
        """
        Busca o index as configurações de uma base de dados Postgres no vetor de configurações "source_databases"  a partir do seu ID.
        :param id_base:
        :return: void
        """
        idex = 0
        # cont=0
        #print("MOBA",self.source_databases)
        for item in self.source_databases:
            if item["id"] != id_base:
                idex = idex + 1

        return idex-1

    def fill_text_fields_base(self):
        """
        Função responsavel por buscar no Json de configurações as iformações da base de dados Postgres, Selecionadaa no
        combobox e preencher os campos do formulario na interfasse grafica.
        :return: void
        """
        current_id = self.combo_box_base.currentData()
        current_config = self.search_base_pg(current_id)

        if current_id != "0":
            print("cuureereree ====", current_id)
            self.nome_base.setText(current_config["nome"])
            self.host.setText(current_config["host"])
            self.porta.setText(current_config["porta"])
            self.base_de_dados.setText(current_config["baseDeDados"])
            self.orgao_responsavel_base.setText(current_config["orgaoResponsavel"])
            self.perios_referencia_base.setText(current_config["periosReferencia"])
            self.data_aquisicao_base.setText(current_config["dataAquisicao"])

            cred = self.credencials.get_credentials(current_id)
            print("creed ", cred)
            self.usuario.setText(cred[0])
            self.senha.setText(cred[1])

        if current_id == "0":
            self.nome_base.clear()
            self.host.clear()
            self.porta.clear()
            self.base_de_dados.clear()
            self.orgao_responsavel_base.clear()
            self.perios_referencia_base.clear()
            self.data_aquisicao_base.clear()
            self.usuario.clear()
            self.senha.clear()

    def fill_text_fields_shp(self):
        """
        Função responsável por buscar no Json de configurações as informações da base de dados Shapefile, Selecionadaa no
        combobox e preencher os campos do formulario na interfasse gráfica.
        :return:  void
        """
        current_id = self.combo_box_shp.currentData()
        current_config = self.search_base_shp(current_id)
        if current_id != "0":
            self.nome_shp.setText(current_config["nome"])
            self.url_dowload.setText(current_config["urlDowload"])
            self.diretorioLocalshp.setFilePath(current_config["diretorioLocal"])
            self.orgao_responsavel_shp.setText(current_config["orgaoResponsavel"])
            self.periodo_referencia_shp.setText(current_config["periosReferencia"])
            self.data_aquisicao_shp.setText(current_config["dataAquisicao"])

        if current_id == "0":
            self.nome_shp.clear()
            self.url_dowload.clear()
            # self.diretorioLocalshp.
            self.orgao_responsavel_shp.clear()
            self.periodo_referencia_shp.clear()
            self.data_aquisicao_shp.clear()

    def fill_combo_box_geocoding_server(self):
        """
        Preenche combobox com as opções de Servidores de Geocodificação.
        :return:
        """
        self.combo_box_servico_geocod.addItem("Google", 0)
        self.combo_box_servico_geocod.addItem("Nominatim (OpenStreetMap)", 1)
        self.combo_box_servico_geocod.addItem("IBGE", 2)

    def save_geocoding_key(self):
        """
        Método responsável por pegar a chave do servidor de Geocodificação digitado na interface e salvar na chache do QGIS.
        :return: void
        """
        current_opt = self.combo_box_servico_geocod.currentData()
        current_opt_text = self.combo_box_servico_geocod.currentText()
        key = self.key_geo_cod.text()
        self.credencials.store_current_geocoding_server([current_opt_text,current_opt])
        self.credencials.store_keys(str(current_opt), key)

    def set_config(self):
        """
        Método responsável por pegar a nova chave do servidor de Geocodificação digitado na interface e modificar/salvar na chache do QGIS.
        :return: void
        """
        current_op = self.credencials.get_current_geocoding_server()
        current_key = self.credencials.get_key(current_op[1])
        self.combo_box_servico_geocod(current_op[1])
        self.key_geo_cod.setText(current_key)


    def back(self):
        self.hide()
        self.back_window.emit()

    def next(self):
        self.hide()
        self.continue_window.emit()

    def hideLayerConfBase(self):
        """
        Renderisa a janela de configuração de camadas das bases PostgreSQL.
        :return: void
        """

        self.save_settings()
        id_current_db = self.combo_box_base.currentData()

        if id_current_db =="0":
            id_current_db = self.newbdID

        print("curreert",type(id_current_db))
        if id_current_db != "0":
            d = ConfigLayers("bd", id_current_db)
            d.exec_()

    def hideLayerConfShp(self):

        """
        Renderisa a janela de configuração de camadas das bases Shapefile.
        :return: void
        """
        self.save_settings()
        id_current_shp = self.combo_box_shp.currentData()

        if id_current_shp == "0":
            id_current_shp = self.newshpID

        print("curreert-SHP", id_current_shp)
        if id_current_shp != "0" and self.nome_shp.text() !="" :
            d = ConfigLayers("shp", id_current_shp)
            d.exec_()

    def hiderheader(self):
        """

        :return:
        """
        d = ReportGenerator()
        d.exec_()

    def message(self):
        """
        Testa se a conexão com o banco de dado foi feita com sucesso.
        :return: void.
        """
        msg = QMessageBox(self)
        host = self.host.text()
        porta = self.porta.text()
        base_de_dados = self.base_de_dados.text()
        usuario = self.usuario.text()
        senha = self.senha.text()

        try:
            conn = DbConnection(host, porta, base_de_dados, usuario, senha)
            if conn.testConnection():
                msg.information(self, "Conexão com Banco de dados", "Conexão feita com sucesso!")
            else:
                msg.critical(self, "Conexão com Banco de dados", "Falha ao conectar com o banco de dados!")

        except Exception as error:
            msg.critical(self, "Conexão com Banco de dados", "Falha ao conectar com o banco de dados!")







