import sys
import os.path
import os

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QComboBox
from qgis.gui import QgsFileWidget, QgsDateTimeEdit
from qgis.core import QgsVectorLayer, QgsDataSourceUri

from .config_layers import ConfigLayers
from .json_tools import JsonTools
from .env_tools import EnvTools

from ..screens.report_generator import ReportGenerator
from ..databases.db_connection import DbConnection
from ..utils.default_sld import slddefaultlayers
from ..utils.wfs_to_geopandas import WfsOperations


class ConfigWindow(QtWidgets.QDialog):
    """Classe reponsavel por manipular a janela de configuração principal"""

    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self):
        super(ConfigWindow, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'config_window.ui'), self)
        self.settings = JsonTools()
        self.credencials = EnvTools()
        self.fill_path_json()
        self.path_json_mudou_flag = 0
        self.source_databases = self.settings.get_config_database()
        self.source_wfs = self.settings.get_config_wfs()
        self.source_shp = self.settings.get_config_shapefile()
        self.fill_combo_box_base()
        self.fill_combo_box_wfs()
        self.fill_combo_box_shp()
        self.fill_combo_box_geocoding_server()
        self.fill_basemap()
        self.fill_sld_default_layers()

        self.newbdID = ''
        self.newshpID = ''
        self.wfs_data = ''
        self.fill_mandatory_layers()
        self.control_problem = 0
        self.btn_cancelar.clicked.connect(self.back)
        self.btn_salvar.clicked.connect(self.save_settings)
        self.btn_reset_default_layers.clicked.connect(self.reset_default_layers)
        self.btn_get_wfs.clicked.connect(self.handle_wfs)
        self.test_conect.clicked.connect(self.message)
        self.testar_base_carregar_camadas.clicked.connect(self.hideLayerConfBase)
        #self.testar_shp_carregar_camadas.clicked.connect(self.hideLayerConfShp)
        self.combo_box_base.activated.connect(self.fill_text_fields_base)
        self.combo_box_shp.activated.connect(self.fill_text_fields_shp)
        self.delete_sh.clicked.connect(self.delete_shp)
        self.btn_delete_wfs.clicked.connect(self.delete_wfs_config)
        self.delete_base.clicked.connect(self.delete_bd)
        self.combo_wfs.activated.connect(self.fill_data_wfs)

        self.comboBox_base_lpm_hom.currentIndexChanged.connect(self.add_action_lpm_homologada)
        self.comboBox_base_lpm_n_hom.currentIndexChanged.connect(self.add_action_lpm_nao_homologada)
        self.comboBox_base_ltm_hom.currentIndexChanged.connect(self.add_action_ltm_homologada)
        self.comboBox_base_ltm_n_hom.currentIndexChanged.connect(self.add_action_ltm_nao_homologada)
        self.comboBox_base_area_uniao.currentIndexChanged.connect(self.add_action_area_uniao)
        self.comboBox_base_area_uniao_n_hom.currentIndexChanged.connect(self.add_action_area_uniao_n_hom)

        self.comboBox_base_lltm_n_hom.currentIndexChanged.connect(self.add_action_lltm_n_hom)
        self.comboBox_base_lltm_hom.currentIndexChanged.connect(self.add_action_lltm_hom)
        self.comboBox_base_lmeo_hom.currentIndexChanged.connect(self.add_action_lmeo_hom)
        self.comboBox_base_lmeo_n_hom.currentIndexChanged.connect(self.add_action_lmeo_n_hom)

        self.groupBox_area_uniao.clicked.connect(self.add_action_area_uniao)
        self.groupBox_lmeo_hom.clicked.connect(self.add_action_lmeo_hom)
        self.groupBox_lltm_hom.clicked.connect(self.add_action_lltm_hom)
        self.groupBox_lpm_hom.clicked.connect(self.add_action_lpm_homologada)
        self.groupBox_ltm_hom.clicked.connect(self.add_action_ltm_homologada)
        self.groupBox_area_uniao_n_hom.clicked.connect(self.add_action_area_uniao_n_hom)
        self.groupBox_lmeo_n_hom.clicked.connect(self.add_action_lmeo_n_hom)
        self.groupBox_lltm_n_hom.clicked.connect(self.add_action_lltm_n_hom)
        self.groupBox_lpm_n_hom.clicked.connect(self.add_action_lpm_nao_homologada)
        self.groupBox_ltm_n_hom.clicked.connect(self.add_action_ltm_nao_homologada)

        self.path_json.fileChanged.connect(self.path_mudou)
        self._list = []

        if self.combo_box_shp.currentIndex() == 0:
            self.delete_sh.setEnabled(False)
        if self.combo_box_base.currentIndex() == 0:
            self.delete_base.setEnabled(False)

        self.combo_box_shp.currentIndexChanged.connect(self.enable_disable_delete_shp)
        self.combo_box_base.currentIndexChanged.connect(self.enable_disable_delete_bd)
        self.combo_wfs.currentIndexChanged.connect(self.handle_combo_wfs)
        # Signal para tratar click no tabWidget
        self.tabWidget.tabBarClicked.connect(self.handle_tabwidget)

    def save_bd_config_json(self):
        """
        Método responsável pegar da interface as informações configuração de base de dados do PostgreSQL e salvar no Json de configuração.
        @return: void
        """
        confg_dic = {}
        id_current_db = self.combo_box_base.currentData()

        config_db = self.settings.get_config_database()
        config = {}
        for item in config_db:
            if item["id"] == id_current_db:
                config = item

        if config != confg_dic:
            confg_dic = config

        confg_dic["id"] = ""
        confg_dic["tipo"] = "pg"
        confg_dic["nome"] = self.nome_base.text()
        confg_dic["host"] = self.host.text()
        confg_dic["porta"] = self.porta.text()
        confg_dic["baseDeDados"] = self.base_de_dados.text()
        confg_dic["orgaoResponsavel"] = self.orgao_responsavel_base.text()

        dt = self.periodos_referencia_base.dateTime()
        dt_string = dt.toString(self.periodos_referencia_base.displayFormat())
        confg_dic["periodosReferencia"] = dt_string

        dt = self.data_aquisicao_base.dateTime()
        dt_string = dt.toString(self.data_aquisicao_base.displayFormat())
        confg_dic["dataAquisicao"] = dt_string

        confg_dic["descricao"] = self.textEdit_bd.toPlainText()

        if self.combo_box_base.currentData() == "0":
            if confg_dic["nome"] == "" and self.tabWidget.currentIndex() == 1:
                msg = QMessageBox(self)
                msg.critical(self, "Erro", "Está faltando o nome da base de dados!")
                self.control_problem = 1
            if confg_dic["nome"] != "":
                id = self.settings.insert_database_pg(confg_dic)
                self.newbdID = id
                self.source_databases.append(confg_dic)
                self.combo_box_base.addItem(self.nome_base.text(), id)
                self.credencials.store_credentials(id, self.usuario.text(), self.senha.text())
               # msg.information(self, "Banco de dados", "Banco de dados adcionado com sucesso!")
                self.combo_box_base.setCurrentText(self.nome_base.text())
                confg_dic = {}

        else:
            if confg_dic["nome"] == "" and self.tabWidget.currentIndex() == 1:
                msg = QMessageBox(self)
                msg.critical(self, "Erro", "Está faltando o nome da base de dados!")
                self.control_problem = 1

            if confg_dic["nome"] != "":
                index = self.search_index_base_pg(id_current_db)

                self.source_databases[index] = confg_dic
                self.settings.edit_database(id_current_db, confg_dic)
                self.credencials.edit_credentials(id_current_db, self.usuario.text(), self.senha.text())
                self.combo_box_base.setCurrentText(self.nome_base.text())
                #self.credencials.store_credentials(id_current_db, self.usuario.text(), self.senha.text())
                #msg.information(self,"Banco de dados" ,"Banco de dados editado com sucesso!")
                confg_dic = {}

    def save_settings(self):
        """
        Salva as configurações de PosgreSQL e ShapeFile no Json de configuração. Executa os metodos: "save_bd_config_json" e "save_shp_config_json"
        @return:
        """
        # self.fill_mandatory_layers()

        self.save_bd_config_json()
        self.save_shp_config_json()
        self.save_mandatory_layers()
        self.save_geocoding_key()
        self.save_basemap()
        self.save_sld_default_layers()
        self.save_wfs_config()

        self.store_path_json()
        if self.path_json_mudou_flag == 1:
            msg = QMessageBox(self)
            msg.warning(self, "Atenção!", "Você mudou a fonte de curadoria. Por Favor, reinicie o plugin para que as alterações entrem e vigor.")
            self.path_json_mudou_flag == 0


        self.fill_mandatory_layers_from_json_conf()

        btn = self.sender()
        btn_name = btn.objectName()
        if self.control_problem == 0:
            if btn_name =="btn_salvar":
                msg = QMessageBox(self)
                msg.information(self, "Salvar Configurações", "As configurações foram salvas com sucesso!")
        self.control_problem = 0

    def save_shp_config_json(self):
        """
        Método responsável pegar da interface as informações configuração de base de dados Shapefile e salvar no Json de configuração.
        @return:
        """
        id_current_db = self.combo_box_shp.currentData()
        current_config = self.search_base_shp(id_current_db)
        confg_dic = {}

        if current_config != confg_dic:
            confg_dic = current_config

        confg_dic["id"] = ""
        confg_dic["tipo"] = "shp"
        confg_dic["nome"] = self.nome_shp.text()
        confg_dic["nomeFantasiaCamada"] = self.nome_shp.text()
        confg_dic["urlDowload"] = self.url_dowload.text()
        confg_dic["diretorioLocal"] = self.diretorioLocalshp.filePath()
        confg_dic["orgaoResponsavel"] = self.orgao_responsavel_shp.text()
        confg_dic["aproximacao"] = [self.faixa_proximidade.value()]
        dt = self.periodo_referencia_shp.dateTime()
        dt_string = dt.toString(self.periodo_referencia_shp.displayFormat())
        confg_dic["periodosReferencia"] = dt_string

        dt = self.data_aquisicao_shp.dateTime()
        dt_string = dt.toString(self.data_aquisicao_shp.displayFormat())
        confg_dic["dataAquisicao"] = dt_string

        confg_dic["descricao"] = self.textEdit_shp.toPlainText()
        stryle = [{
             "line_style": "",
                "line_color": "",
                "width_border": "",
                "style": "",
                "color": "",
                "stylePath" : self.style_path.filePath(),
        }]

        confg_dic["estiloCamadas"] = stryle

        if self.combo_box_shp.currentData() == "0":
            if confg_dic["nome"] == "" and self.tabWidget.currentIndex() == 0:
                msg = QMessageBox(self)
                msg.critical(self, "Erro", "Está faltando o nome da base de dados!")
                self.control_problem = 1
            if confg_dic["nome"] != "":
                id = self.settings.insert_database_pg(confg_dic)
                self.newshpID = id

                self.source_shp.append(confg_dic)
                self.combo_box_shp.addItem(self.nome_shp.text(), id)
                #msg.information(self, "ShapeFile", "Shapefile adcionado com sucesso!")
                self.combo_box_shp.setCurrentText(self.nome_shp.text())
                # self.credencials.store_credentials(id, self.usuario.text(), self.senha.text())
                confg_dic = {}

        else:
            if confg_dic["nome"] == "" and self.tabWidget.currentIndex() == 0:
                msg = QMessageBox(self)
                msg.critical(self, "Erro", "Está faltando o nome da base de dados!")
                self.control_problem = 1

            if confg_dic["nome"] != "":
                index = self.search_index_base_shp(id_current_db)

                self.source_shp[index] = confg_dic
                self.settings.edit_database(id_current_db, confg_dic)
                self.combo_box_shp.setCurrentText(self.nome_shp.text())
                #msg.information(self, "ShapeFile", "Shapefile editado com sucesso!")
                # self.credencials.edit_credentials(id_current_db, self.usuario.text(), self.senha.text())
                confg_dic = {}

    def save_basemap(self):
        json_complete = self.settings.get_json()

        selected_basemap = self.cbx_basemap.currentText()
        for value in json_complete['basemap']:
            if value[0] == selected_basemap:
                value[2] = "True"
            else:
                value[2] = "False"

        self.settings.insert_data(json_complete)

    def save_sld_default_layers(self):
        json_complete = self.settings.get_json()

        default_input_polygon = self.qfw_entrada_poligono.filePath()
        default_input_line = self.qfw_entrada_linha.filePath()
        default_input_point = self.qfw_entrada_ponto.filePath()

        buffer = self.qfw_buffer.filePath()

        overlay_input_polygon = self.qfw_sobreposicao_poligono.filePath()
        overlay_input_line = self.qfw_sobreposicao_linha.filePath()
        overlay_input_point = self.qfw_sobreposicao_ponto.filePath()

        # Tratando campo de sld para input polígono
        if len(default_input_polygon) == 0:
            json_complete['sld_default_layers']['default_input_polygon'] = slddefaultlayers.POLYGON_SLD_INPUT.value
        else:
            json_complete['sld_default_layers']['default_input_polygon'] = default_input_polygon

        # Tratando campo de sld para input linha
        if len(default_input_line) == 0:
            json_complete['sld_default_layers']['default_input_line'] = slddefaultlayers.LINE_SLD_INPUT.value
        else:
            json_complete['sld_default_layers']['default_input_line'] = default_input_line

        # Tratando campo de sld para input ponto
        if len(default_input_point) == 0:
            json_complete['sld_default_layers']['default_input_point'] = slddefaultlayers.POINT_SLD_INPUT.value
        else:
            json_complete['sld_default_layers']['default_input_point'] = default_input_point

        # Tratando campo de sld para buffer
        if len(buffer) == 0:
            json_complete['sld_default_layers']['buffer'] = slddefaultlayers.BUFFER_SLD.value
        else:
            json_complete['sld_default_layers']['buffer'] = buffer

        # Tratando campo de sld para camada sobreposição Polígono
        if len(overlay_input_polygon) == 0:
            json_complete['sld_default_layers']['overlay_input_polygon'] = slddefaultlayers.POLYGON_SLD_OVERLAY.value
        else:
            json_complete['sld_default_layers']['overlay_input_polygon'] = overlay_input_polygon

        # Tratando campo de sld para camada sobreposição Linha
        if len(overlay_input_line) == 0:
            json_complete['sld_default_layers']['overlay_input_line'] = slddefaultlayers.LINE_SLD_OVERLAY.value
        else:
            json_complete['sld_default_layers']['overlay_input_line'] = overlay_input_line

        # Tratando campo de sld para camada sobreposição Ponto
        if len(overlay_input_point) == 0:
            json_complete['sld_default_layers']['overlay_input_point'] = slddefaultlayers.POINT_SLD_OVERLAY.value
        else:
            json_complete['sld_default_layers']['overlay_input_point'] = overlay_input_point

        self.settings.insert_data(json_complete)

    def fill_sld_default_layers(self):
        json_complete = self.settings.get_json()

        if 'sld_default_layers' in json_complete and 'default_input_polygon' in json_complete['sld_default_layers']:
            self.qfw_entrada_poligono.setFilePath(json_complete['sld_default_layers']['default_input_polygon'])

        if 'sld_default_layers' in json_complete and 'default_input_line' in json_complete['sld_default_layers']:
            self.qfw_entrada_linha.setFilePath(json_complete['sld_default_layers']['default_input_line'])

        if 'sld_default_layers' in json_complete and 'default_input_point' in json_complete['sld_default_layers']:
            self.qfw_entrada_ponto.setFilePath(json_complete['sld_default_layers']['default_input_point'])

        if 'sld_default_layers' in json_complete and 'buffer' in json_complete['sld_default_layers']:
            self.qfw_buffer.setFilePath(json_complete['sld_default_layers']['buffer'])

        if 'sld_default_layers' in json_complete and 'overlay_input_polygon' in json_complete['sld_default_layers']:
            self.qfw_sobreposicao_poligono.setFilePath(json_complete['sld_default_layers']['overlay_input_polygon'])

        if 'sld_default_layers' in json_complete and 'overlay_input_line' in json_complete['sld_default_layers']:
            self.qfw_sobreposicao_linha.setFilePath(json_complete['sld_default_layers']['overlay_input_line'])

        if 'sld_default_layers' in json_complete and 'overlay_input_point' in json_complete['sld_default_layers']:
            self.qfw_sobreposicao_ponto.setFilePath(json_complete['sld_default_layers']['overlay_input_point'])

    def reset_default_layers(self):
        self.qfw_entrada_poligono.setFilePath(slddefaultlayers.POLYGON_SLD_INPUT.value)
        self.qfw_entrada_linha.setFilePath(slddefaultlayers.LINE_SLD_INPUT.value)
        self.qfw_entrada_ponto.setFilePath(slddefaultlayers.POLYGON_SLD_INPUT.value)
        self.qfw_buffer.setFilePath(slddefaultlayers.BUFFER_SLD.value)
        self.qfw_sobreposicao_poligono.setFilePath(slddefaultlayers.POLYGON_SLD_OVERLAY.value)
        self.qfw_sobreposicao_linha.setFilePath(slddefaultlayers.LINE_SLD_OVERLAY.value)
        self.qfw_sobreposicao_ponto.setFilePath(slddefaultlayers.POINT_SLD_OVERLAY.value)

    def fill_basemap(self):
        json_basemap = self.settings.get_config_basemap()

        basemap_name = [x[0] for x in json_basemap]
        self.cbx_basemap.addItems(basemap_name)

        selected_basemap: int = None
        for index, value in enumerate(json_basemap):
            if value[2] == "True":
                selected_basemap = index

        self.cbx_basemap.setCurrentIndex(selected_basemap)

    def fill_combo_box_base(self):
        """
        Preenche o combox com bases PostgreSQl cadastradas e presentes no Json de configuração.
        @return: void
        """
        self.combo_box_base.setItemData(0, "0")
        if len(self.source_databases) > 0:
            for item in self.source_databases:
                self.combo_box_base.addItem(item["nome"], item["id"])

    def fill_combo_box_wfs(self):
        """
        Preenche o combox com bases PostgreSQl cadastradas e presentes no Json de configuração.
        @return: void
        """
        self.combo_wfs.setItemData(0, "0")
        if len(self.source_wfs) > 0:
            for item in self.source_wfs:
                self.combo_wfs.addItem(item["nome"], item["id"])

    def fill_combo_box_shp(self):
        """
        Preenche o combox com bases ShapeFile cadastradas e presentes no Json de configuração.
        @return:
        """
        self.combo_box_shp.setItemData(0, "0")
        if len(self.source_shp) > 0:
            for item in self.source_shp:
                self.combo_box_shp.addItem(item["nome"], item["id"])

    def search_base_pg(self, id_base):
        """
        Busca as configurações de uma base de dados PostgreSQL apartir do seu ID
        @param id_base: ID da base dados
        @return:
        """
        config = {}
        for item in self.source_databases:
            if item["id"] == id_base:
                config = item

        return config

    def search_base_shp(self, id_base):
        """
        Busca as configurações de uma base de dados Shapefile a partir do seu ID.
        @param id_base: ID da base dados
        @return:
        """
        config = {}
        for item in self.source_shp:
            if item["id"] == id_base:
                config = item

        return config

    def search_index_base_shp(self, id_base):
        """
        Busca o index as configurações de uma base de dados Shapefile no vetor de configurações "source_shp"  a partir do seu ID.
        @param id_base: ID da base dados
        @return:
        """
        idex = 0
        for item in self.source_shp:
            if item["id"] != id_base:
                idex = idex + 1

        return idex - 1

    def search_index_base_pg(self, id_base):
        """
        Busca o index as configurações de uma base de dados Postgres no vetor de configurações "source_databases"  a partir do seu ID.
        @param id_base:
        @return: void
        """
        idex = 0
        # cont=0
        for item in self.source_databases:
            if item["id"] != id_base:
                idex = idex + 1

        return idex - 1

    def fill_text_fields_base(self):
        """
        Função responsavel por buscar no Json de configurações as iformações da base de dados Postgres, Selecionadaa no
        combobox e preencher os campos do formulario na interfasse grafica.
        @return: void
        """
        current_id = self.combo_box_base.currentData()
        current_config = self.search_base_pg(current_id)

        if current_id != "0":
            self.nome_base.setText(current_config["nome"])
            self.host.setText(current_config["host"])
            self.porta.setText(current_config["porta"])
            self.base_de_dados.setText(current_config["baseDeDados"])
            self.orgao_responsavel_base.setText(current_config["orgaoResponsavel"])

            get_date = current_config["periodosReferencia"].split("/")
            date = QtCore.QDate(int(get_date[2]), int(get_date[1]), int(get_date[0]))
            self.periodos_referencia_base.setDate(date)

            get_date = current_config["dataAquisicao"].split("/")
            date = QtCore.QDate(int(get_date[2]), int(get_date[1]), int(get_date[0]))
            self.data_aquisicao_base.setDate(date)

            self.textEdit_bd.setText(current_config["descricao"])

            cred = self.credencials.get_credentials(current_id)

            self.usuario.setText(cred[0])
            self.senha.setText(cred[1])

        if current_id == "0":
            self.nome_base.clear()
            self.host.clear()
            self.porta.clear()
            self.base_de_dados.clear()
            self.orgao_responsavel_base.clear()
            #self.periodos_referencia_base.clear()
            #self.data_aquisicao_base.clear()
            self.usuario.clear()
            self.senha.clear()
            self.textEdit_bd.clear()

    def fill_text_fields_shp(self):
        """
        Função responsável por buscar no Json de configurações as informações da base de dados Shapefile, Selecionadaa no
        combobox e preencher os campos do formulario na interfasse gráfica.
        @return:  void
        """
        current_id = self.combo_box_shp.currentData()
        current_config = self.search_base_shp(current_id)
        if current_id != "0":
            self.nome_shp.setText(current_config["nome"])
            self.url_dowload.setText(current_config["urlDowload"])
            self.diretorioLocalshp.setFilePath(current_config["diretorioLocal"])
            self.orgao_responsavel_shp.setText(current_config["orgaoResponsavel"])

            get_date = current_config["periodosReferencia"].split("/")
            date = QtCore.QDate(int(get_date[2]), int(get_date[1]), int(get_date[0]))
            self.periodo_referencia_shp.setDate(date)

            get_date = current_config["dataAquisicao"].split("/")
            date = QtCore.QDate(int(get_date[2]), int(get_date[1]), int(get_date[0]))
            self.data_aquisicao_shp.setDate(date)

            style = current_config["estiloCamadas"][0]
            self.style_path.setFilePath(style["stylePath"])
            self.textEdit_shp.setText(current_config["descricao"])
            self.faixa_proximidade.setValue(current_config["aproximacao"][0])

        if current_id == "0":
            self.nome_shp.clear()
            self.url_dowload.clear()
            self.diretorioLocalshp.setFilePath("")
            self.style_path.setFilePath("")
            self.orgao_responsavel_shp.clear()
            self.textEdit_shp.clear()
            #self.periodo_referencia_shp.clear()
            #self.data_aquisicao_shp.clear()

    def fill_combo_box_geocoding_server(self):
        """
        Preenche combobox com as opções de Servidores de Geocodificação.
        @return:
        """
        self.combo_box_servico_geocod.addItem("Google", 0)
        self.combo_box_servico_geocod.addItem("Nominatim (OpenStreetMap)", 1)
       #self.combo_box_servico_geocod.addItem("IBGE", 2)
        self.set_config()


    def save_geocoding_key(self):
        """
        Método responsável por pegar a chave do servidor de Geocodificação digitado na interface e salvar na chache do QGIS.
        @return: void
        """
        current_opt = self.combo_box_servico_geocod.currentData()
        current_opt_text = self.combo_box_servico_geocod.currentText()
        key = self.key_geo_cod.text()

        self.credencials.store_current_geocoding_server(current_opt)
        self.credencials.store_keys(str(current_opt), key)

    def set_config(self):
        """
        Método responsável por pegar a nova chave do servidor de Geocodificação digitado na interface e modificar/salvar na chache do QGIS.
        @return: void
        """
        current_op = self.credencials.get_current_geocoding_server()
        current_key = self.credencials.get_key(current_op)

        self.combo_box_servico_geocod.setCurrentIndex(int(current_op))
        self.key_geo_cod.setText(current_key)

    def back(self):
        self.hide()

    def next(self):
        self.hide()
        self.continue_window.emit()

    def hideLayerConfBase(self):
        """
        Renderisa a janela de configuração de camadas das bases PostgreSQL.
        @return: void
        """
        self.save_settings()
        id_current_db = self.combo_box_base.currentData()

        if id_current_db == "0":
            id_current_db = self.newbdID

        if id_current_db != "0":
            d = ConfigLayers("bd", id_current_db, self.usuario.text(), self.senha.text())
            d.exec_()

    def hideLayerConfShp(self):

        """
        Renderisa a janela de configuração de camadas das bases Shapefile.
        @return: void
        """
        self.save_settings()
        id_current_shp = self.combo_box_shp.currentData()

        if id_current_shp == "0":
            id_current_shp = self.newshpID

        if id_current_shp != "0" and self.nome_shp.text() != "":
            d = ConfigLayers("shp", id_current_shp)
            d.exec_()

    def hiderheader(self):
        """

        @return:
        """
        d = ReportGenerator()
        d.exec_()

    def message(self):
        """
        Testa se a conexão com o banco de dado foi feita com sucesso.
        @return: void.
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

    def fill_mandatory_layers_from_json_conf(self):
        camada_obrig = self.settings.get_camadas_base_obrigatoria()
        #pg = self.settings.get_config_database()
        #shp = self.settings.get_config_shapefile()
        source_databases = self.settings.get_config_database()
        source_shp = self.settings.get_config_shapefile()
        source_shp = self.settings.get_config_shapefile()

        self.comboBox_base_lpm_hom.clear()
        self.comboBox_base_lpm_n_hom.clear()
        self.comboBox_base_ltm_hom.clear()
        self.comboBox_base_ltm_n_hom.clear()
        self.comboBox_base_area_uniao.clear()
        self.comboBox_base_area_uniao_n_hom.clear()
        self.comboBox_base_lltm_n_hom.clear()
        self.comboBox_base_lltm_hom.clear()
        self.comboBox_base_lmeo_hom.clear()
        self.comboBox_base_lmeo_n_hom.clear()

        for item in source_databases:
            self.comboBox_base_lpm_hom.addItem(item["nome"] + " " + "(PostgreSQL)", [item["id"],item["tipo"]])
            self.comboBox_base_lpm_n_hom.addItem(item["nome"] + " " + "(PostgreSQL)", [item["id"],item["tipo"]])
            self.comboBox_base_ltm_hom.addItem(item["nome"] + " " + "(PostgreSQL)", [item["id"],item["tipo"]])
            self.comboBox_base_ltm_n_hom.addItem(item["nome"] + " " + "(PostgreSQL)", [item["id"],item["tipo"]])
            self.comboBox_base_area_uniao.addItem(item["nome"] + " " + "(PostgreSQL)", [item["id"],item["tipo"]])
            self.comboBox_base_area_uniao_n_hom.addItem(item["nome"] + " " + "(PostgreSQL)", [item["id"],item["tipo"]])
            self.comboBox_base_lltm_n_hom.addItem(item["nome"] + " " + "(PostgreSQL)", [item["id"],item["tipo"]])
            self.comboBox_base_lltm_hom.addItem(item["nome"] + " " + "(PostgreSQL)", [item["id"],item["tipo"]])
            self.comboBox_base_lmeo_hom.addItem(item["nome"] + " " + "(PostgreSQL)", [item["id"],item["tipo"]])
            self.comboBox_base_lmeo_n_hom.addItem(item["nome"] + " " + "(PostgreSQL)", [item["id"],item["tipo"]])

        for item in source_shp:
            self.comboBox_base_lpm_hom.addItem(item["nome"] + " " + "(ShapeFile)", [item["id"],item["tipo"]])
            self.comboBox_base_lpm_n_hom.addItem(item["nome"] + " " + "(ShapeFile)", [item["id"],item["tipo"]])
            self.comboBox_base_ltm_hom.addItem(item["nome"] + " " + "(ShapeFile)", [item["id"],item["tipo"]])
            self.comboBox_base_ltm_n_hom.addItem(item["nome"] + " " + "(ShapeFile)", [item["id"],item["tipo"]])
            self.comboBox_base_area_uniao.addItem(item["nome"] + " " + "(ShapeFile)", [item["id"],item["tipo"]])
            self.comboBox_base_area_uniao_n_hom.addItem(item["nome"] + " " + "(ShapeFile)", [item["id"],item["tipo"]])
            self.comboBox_base_lltm_n_hom.addItem(item["nome"] + " " + "(ShapeFile)", [item["id"],item["tipo"]])
            self.comboBox_base_lltm_hom.addItem(item["nome"] + " " + "(ShapeFile)", [item["id"],item["tipo"]])
            self.comboBox_base_lmeo_hom.addItem(item["nome"] + " " + "(ShapeFile)",[item["id"],item["tipo"]])
            self.comboBox_base_lmeo_n_hom.addItem(item["nome"] + " " + "(ShapeFile)", [item["id"],item["tipo"]])

        if "area_homologada" in camada_obrig:
            base_config = self.search_base_pg(camada_obrig["area_homologada"][0])
            if base_config == {}:
                 base_config = self.search_base_shp(camada_obrig["area_homologada"][0])

            if "tipo" in base_config:
                if base_config["tipo"] == "pg":
                    self.comboBox_camada_area_uniao.clear()
                    if "tabelasCamadas" in base_config:
                        for item_camada in base_config["tabelasCamadas"]:
                            self.comboBox_camada_area_uniao.addItem(item_camada)

                        self.comboBox_base_area_uniao.setCurrentText(base_config["nome"] + " (PostgreSQL)")

                if base_config["tipo"] == "shp":
                    self.comboBox_camada_area_uniao.clear()
                    self.comboBox_camada_area_uniao.addItem(base_config["nome"])
                    self.comboBox_base_area_uniao.setCurrentText(base_config["nome"] + " (ShapeFile)")

                self.comboBox_camada_area_uniao.setCurrentText(camada_obrig["area_homologada"][1])
                self.groupBox_area_uniao.setChecked(True)

            #LLTM Homologada:

            if "lltm_homologada" in camada_obrig:
                base_config = self.search_base_pg(camada_obrig["lltm_homologada"][0])

                if base_config == {}:
                    base_config = self.search_base_shp(camada_obrig["lltm_homologada"][0])

                if "tipo" in base_config:
                    if base_config["tipo"] == "pg":
                        self.comboBox_camada_lltm_hom.clear()
                        if "tabelasCamadas" in base_config:
                            for item_camada in base_config["tabelasCamadas"]:
                                self.comboBox_camada_lltm_hom.addItem(item_camada)

                            self.comboBox_base_lltm_hom.setCurrentText(base_config["nome"] + " (PostgreSQL)")

                    if base_config["tipo"] == "shp":
                        self.comboBox_camada_lltm_hom.clear()
                        self.comboBox_camada_lltm_hom.addItem(base_config["nome"])
                        self.comboBox_base_lltm_hom.setCurrentText(base_config["nome"] + " (ShapeFile)")

                    self.comboBox_camada_lltm_hom.setCurrentText(camada_obrig["lltm_homologada"][1])
                    self.groupBox_lltm_hom.setChecked(True)

            #LMEO homologada
            if "lmeo_homologada" in camada_obrig:
                base_config = self.search_base_pg(camada_obrig["lmeo_homologada"][0])
                if base_config == {}:
                    base_config = self.search_base_shp(camada_obrig["lmeo_homologada"][0])

                if "tipo" in base_config:
                    if base_config["tipo"] == "pg":
                        self.comboBox_camada_lmeo_hom.clear()
                        if "tabelasCamadas" in base_config:
                            for item_camada in base_config["tabelasCamadas"]:
                                self.comboBox_camada_lmeo_hom.addItem(item_camada)

                            self.comboBox_base_lmeo_hom.setCurrentText(base_config["nome"] + " (PostgreSQL)")

                    if base_config["tipo"] == "shp":
                        self.comboBox_camada_lmeo_hom.clear()
                        self.comboBox_camada_lmeo_hom.addItem(base_config["nome"])
                        self.comboBox_base_lmeo_hom.setCurrentText(base_config["nome"] + " (ShapeFile)")

                    self.comboBox_camada_lmeo_hom.setCurrentText(camada_obrig["lmeo_homologada"][1])
                    self.groupBox_lmeo_hom.setChecked(True)

            #LPM Homologada

            if "lpm_homologada" in camada_obrig:
                base_config = self.search_base_pg(camada_obrig["lpm_homologada"][0])

                if base_config == {}:
                    base_config = self.search_base_shp(camada_obrig["lpm_homologada"][0])

                if "tipo" in base_config:
                    if base_config["tipo"] == "pg":
                        self.comboBox_camada_lpm_hom.clear()
                        if "tabelasCamadas" in base_config:
                            for item_camada in base_config["tabelasCamadas"]:
                                self.comboBox_camada_lpm_hom.addItem(item_camada)

                            self.comboBox_base_lpm_hom.setCurrentText(base_config["nome"] + " (PostgreSQL)")

                    if base_config["tipo"] == "shp":
                        self.comboBox_camada_lpm_hom.clear()
                        self.comboBox_camada_lpm_hom.addItem(base_config["nome"])
                        self.comboBox_base_lpm_hom.setCurrentText(base_config["nome"] + " (ShapeFile)")

                    self.comboBox_camada_lpm_hom.setCurrentText(camada_obrig["lpm_homologada"][1])
                    self.groupBox_lpm_hom.setChecked(True)

            #LTM Homologada
            if "ltm_homologada" in camada_obrig:
                base_config = self.search_base_pg(camada_obrig["ltm_homologada"][0])

                if base_config == {}:
                    base_config = self.search_base_shp(camada_obrig["ltm_homologada"][0])

                if "tipo" in base_config:
                    if base_config["tipo"] == "pg":
                        self.comboBox_camada_ltm_hom.clear()
                        if "tabelasCamadas" in base_config:
                            for item_camada in base_config["tabelasCamadas"]:
                                self.comboBox_camada_ltm_hom.addItem(item_camada)

                            self.comboBox_base_ltm_hom.setCurrentText(base_config["nome"] + " (PostgreSQL)")

                    if base_config["tipo"] == "shp":
                        self.comboBox_camada_ltm_hom.clear()
                        self.comboBox_camada_ltm_hom.addItem(base_config["nome"])
                        self.comboBox_base_ltm_hom.setCurrentText(base_config["nome"] + " (ShapeFile)")

                    self.comboBox_camada_ltm_hom.setCurrentText(camada_obrig["ltm_homologada"][1])
                    self.groupBox_ltm_hom.setChecked(True)

            #Area da União não homologada
            if "area_nao_homologada" in camada_obrig:
                base_config = self.search_base_pg(camada_obrig["area_nao_homologada"][0])
                if base_config == {}:
                    base_config = self.search_base_shp(camada_obrig["area_nao_homologada"][0])

                if "tipo" in base_config:
                    if base_config["tipo"] == "pg":
                        self.comboBox_camada_area_uniao_n_hom.clear()
                        if "tabelasCamadas" in base_config:
                            for item_camada in base_config["tabelasCamadas"]:
                                self.comboBox_camada_area_uniao_n_hom.addItem(item_camada)

                            self.comboBox_base_area_uniao_n_hom.setCurrentText(base_config["nome"] + " (PostgreSQL)")

                    if base_config["tipo"] == "shp":
                        self.comboBox_camada_area_uniao_n_hom.clear()
                        self.comboBox_camada_area_uniao_n_hom.addItem(base_config["nome"])
                        self.comboBox_base_area_uniao_n_hom.setCurrentText(base_config["nome"] + " (ShapeFile)")

                    self.comboBox_camada_area_uniao_n_hom.setCurrentText(camada_obrig["area_nao_homologada"][1])
                    self.groupBox_area_uniao_n_hom.setChecked(True)

            #LLTM não homologada
            if "lltm_nao_homologada" in camada_obrig:
                base_config = self.search_base_pg(camada_obrig["lltm_nao_homologada"][0])

                if base_config == {}:
                    base_config = self.search_base_shp(camada_obrig["lltm_nao_homologada"][0])

                if "tipo" in base_config:
                    if base_config["tipo"] == "pg":
                        self.comboBox_camada_lltm_n_hom.clear()
                        if "tabelasCamadas" in base_config:
                            for item_camada in base_config["tabelasCamadas"]:
                                self.comboBox_camada_lltm_n_hom.addItem(item_camada)

                            self.comboBox_base_lltm_n_hom.setCurrentText(base_config["nome"] + " (PostgreSQL)")
                    #
                    if base_config["tipo"] == "shp":
                        self.comboBox_camada_lltm_n_hom.clear()
                        self.comboBox_camada_lltm_n_hom.addItem(base_config["nome"])
                        self.comboBox_base_lltm_n_hom.setCurrentText(base_config["nome"] + " (ShapeFile)")

                    self.comboBox_camada_lltm_n_hom.setCurrentText(camada_obrig["lltm_nao_homologada"][1])
                    self.groupBox_lltm_n_hom.setChecked(True)

            #LPM não homologada
            if "lpm_nao_homologada" in camada_obrig:
                base_config = self.search_base_pg(camada_obrig["lpm_nao_homologada"][0])
                if base_config == {}:
                    base_config = self.search_base_shp(camada_obrig["lpm_nao_homologada"][0])

                if "tipo" in base_config:
                    if base_config["tipo"] == "pg":
                        self.comboBox_camada_lpm_n_hom.clear()
                        if "tabelasCamadas" in base_config:
                            for item_camada in base_config["tabelasCamadas"]:
                                self.comboBox_camada_lpm_n_hom.addItem(item_camada)

                            self.comboBox_base_lpm_n_hom.setCurrentText(base_config["nome"] + " (PostgreSQL)")

                    if base_config["tipo"] == "shp":
                        self.comboBox_camada_lpm_n_hom.clear()
                        self.comboBox_camada_lpm_n_hom.addItem(base_config["nome"])
                        self.comboBox_base_lpm_n_hom.setCurrentText(base_config["nome"] + " (ShapeFile)")

                    self.comboBox_camada_lpm_n_hom.setCurrentText(camada_obrig["lpm_nao_homologada"][1])
                    self.groupBox_lpm_n_hom.setChecked(True)

            #LEMEO não homologada
            if "lmeo_nao_homologada" in camada_obrig:
                base_config = self.search_base_pg(camada_obrig["lmeo_nao_homologada"][0])

                if base_config == {}:
                    base_config = self.search_base_shp(camada_obrig["lmeo_nao_homologada"][0])

                if "tipo" in base_config:
                    if base_config["tipo"] == "pg":
                        self.comboBox_camada_lmeo_n_hom.clear()
                        if "tabelasCamadas" in base_config:
                            for item_camada in base_config["tabelasCamadas"]:
                                self.comboBox_camada_lmeo_n_hom.addItem(item_camada)

                            self.comboBox_base_lmeo_n_hom.setCurrentText(base_config["nome"] + " (PostgreSQL)")

                    if base_config["tipo"] == "shp":
                        self.comboBox_base_lmeo_n_hom.clear()
                        self.comboBox_camada_lmeo_n_hom.addItem(base_config["nome"])
                        self.comboBox_base_lmeo_n_hom.setCurrentText(base_config["nome"] + " (ShapeFile)")

                    self.comboBox_camada_lmeo_n_hom.setCurrentText(camada_obrig["lmeo_nao_homologada"][1])
                    self.groupBox_lmeo_n_hom.setChecked(True)

            #LTM não homologada

            if "ltm_nao_homologada" in camada_obrig:
                base_config = self.search_base_pg(camada_obrig["ltm_nao_homologada"][0])
                if base_config == {}:
                    base_config = self.search_base_shp(camada_obrig["ltm_nao_homologada"][0])

                if "tipo" in base_config:
                    if base_config["tipo"] == "pg":
                        self.comboBox_camada_ltm_n_hom.clear()
                        if "tabelasCamadas" in base_config:
                            for item_camada in base_config["tabelasCamadas"]:
                                self.comboBox_camada_ltm_n_hom.addItem(item_camada)
                            self.comboBox_base_ltm_n_hom.setCurrentText(base_config["nome"] + " (PostgreSQL)")

                    if base_config["tipo"] == "shp":
                        self.comboBox_camada_ltm_n_hom.clear()
                        self.comboBox_camada_ltm_n_hom.addItem(base_config["nome"])
                        self.comboBox_base_ltm_n_hom.setCurrentText(base_config["nome"] + " (ShapeFile)")

                    self.comboBox_camada_ltm_n_hom.setCurrentText(camada_obrig["ltm_nao_homologada"][1])
                    self.groupBox_ltm_n_hom.setCheckable(True)

            # if base_config == {}:
            #     base_config = self.search_base_shp(camada_obrig["area_nao_homologada"][0])
            #
            # if base_config["tipo"] == "pg":
            #     self.comboBox_camada_area_uniao_n_hom.clear()
            #     for item_camada in base_config["TabelasDisponiveis"]:
            #         self.comboBox_camada_area_uniao_n_hom.addItem(item_camada)
            #     self.comboBox_base_area_uniao_n_hom.setCurrentText(base_config["nome"] + " (PostgreSQL)")
            #
            # if base_config["tipo"] == "shp":
            #     self.comboBox_camada_area_uniao_n_hom.clear()
            #     self.comboBox_camada_area_uniao_n_hom.addItem(base_config["nome"])
            #     self.comboBox_base_area_uniao_n_hom.setCurrentText(base_config["nome"] + " (ShapeFile)")
            # print(base_config["nome"])
            # self.comboBox_base_area_uniao_n_hom.setCurrentText(base_config["nome"])

    def fill_mandatory_layers_not_json(self):

        self.comboBox_base_lpm_hom.clear()
        self.comboBox_base_lpm_n_hom.clear()
        self.comboBox_base_ltm_hom.clear()
        self.comboBox_base_ltm_n_hom.clear()
        self.comboBox_base_area_uniao.clear()
        self.comboBox_base_area_uniao_n_hom.clear()
        self.comboBox_base_lltm_n_hom.clear()
        self.comboBox_base_lltm_hom.clear()
        self.comboBox_base_lmeo_hom.clear()
        self.comboBox_base_lmeo_n_hom.clear()

        for item in self.source_databases:
            self.comboBox_base_lpm_hom.addItem(item["nome"] + " " + "(PostgreSQL)", [item["id"],item["tipo"]])
            self.comboBox_base_lpm_n_hom.addItem(item["nome"] + " " + "(PostgreSQL)", [item["id"],item["tipo"]])
            self.comboBox_base_ltm_hom.addItem(item["nome"] + " " + "(PostgreSQL)", [item["id"],item["tipo"]])
            self.comboBox_base_ltm_n_hom.addItem(item["nome"] + " " + "(PostgreSQL)", [item["id"],item["tipo"]])
            self.comboBox_base_area_uniao.addItem(item["nome"] + " " + "(PostgreSQL)", [item["id"],item["tipo"]])
            self.comboBox_base_area_uniao_n_hom.addItem(item["nome"] + " " + "(PostgreSQL)", [item["id"],item["tipo"]])
            self.comboBox_base_lltm_n_hom.addItem(item["nome"] + " " + "(PostgreSQL)", [item["id"],item["tipo"]])
            self.comboBox_base_lltm_hom.addItem(item["nome"] + " " + "(PostgreSQL)", [item["id"],item["tipo"]])
            self.comboBox_base_lmeo_hom.addItem(item["nome"] + " " + "(PostgreSQL)", [item["id"],item["tipo"]])
            self.comboBox_base_lmeo_n_hom.addItem(item["nome"] + " " + "(PostgreSQL)", [item["id"],item["tipo"]])

        for item in self.source_shp:
            self.comboBox_base_lpm_hom.addItem(item["nome"] + " " + "(ShapeFile)", [item["id"],item["tipo"]])
            self.comboBox_base_lpm_n_hom.addItem(item["nome"] + " " + "(ShapeFile)", [item["id"],item["tipo"]])
            self.comboBox_base_ltm_hom.addItem(item["nome"] + " " + "(ShapeFile)", [item["id"],item["tipo"]])
            self.comboBox_base_ltm_n_hom.addItem(item["nome"] + " " + "(ShapeFile)", [item["id"],item["tipo"]])
            self.comboBox_base_area_uniao.addItem(item["nome"] + " " + "(ShapeFile)", [item["id"],item["tipo"]])
            self.comboBox_base_area_uniao_n_hom.addItem(item["nome"] + " " + "(ShapeFile)", [item["id"],item["tipo"]])
            self.comboBox_base_lltm_n_hom.addItem(item["nome"] + " " + "(ShapeFile)", [item["id"],item["tipo"]])
            self.comboBox_base_lltm_hom.addItem(item["nome"] + " " + "(ShapeFile)", [item["id"],item["tipo"]])
            self.comboBox_base_lmeo_hom.addItem(item["nome"] + " " + "(ShapeFile)", [item["id"],item["tipo"]])
            self.comboBox_base_lmeo_n_hom.addItem(item["nome"] + " " + "(ShapeFile)", [item["id"],item["tipo"]])

    def fill_mandatory_layers(self):
        camada_obrig = self.settings.get_camadas_base_obrigatoria()
        self.fill_mandatory_layers_from_json_conf()

    def add_action_lpm_homologada(self):
        try:
            id_base_selec = self.comboBox_base_lpm_hom.currentData()[0]

            base_config = self.search_base_pg(id_base_selec)

            if base_config == {}:
                base_config = self.search_base_shp(id_base_selec)

            if base_config["tipo"] == "pg":
                self.comboBox_camada_lpm_hom.clear()
                for item_camada in base_config["tabelasCamadas"]:
                    self.comboBox_camada_lpm_hom.addItem(item_camada)

            if base_config["tipo"] == "shp":
                self.comboBox_camada_lpm_hom.clear()
                self.comboBox_camada_lpm_hom.addItem(base_config["nome"])

        except Exception as e:
            print(e)
    def add_action_lpm_nao_homologada(self):
        try:
            id_base_selec = self.comboBox_base_lpm_n_hom.currentData()[0]

            base_config = self.search_base_pg(id_base_selec)

            if base_config == {}:
                base_config = self.search_base_shp(id_base_selec)

            if base_config["tipo"] == "pg":
                self.comboBox_camada_lpm_n_hom.clear()
                for item_camada in base_config["tabelasCamadas"]:
                    self.comboBox_camada_lpm_n_hom.addItem(item_camada)

            if base_config["tipo"] == "shp":
                self.comboBox_camada_lpm_n_hom.clear()
                self.comboBox_camada_lpm_n_hom.addItem(base_config["nome"])

        except Exception as e:
            print(e)

    def add_action_ltm_homologada(self):
        try:
            id_base_selec = self.comboBox_base_ltm_hom.currentData()[0]

            base_config = self.search_base_pg(id_base_selec)

            if base_config == {}:
                base_config = self.search_base_shp(id_base_selec)

            if base_config["tipo"] == "pg":
                self.comboBox_camada_ltm_hom.clear()
                for item_camada in base_config["tabelasCamadas"]:
                    self.comboBox_camada_ltm_hom.addItem(item_camada)

            if base_config["tipo"] == "shp":
                self.comboBox_camada_ltm_hom.clear()
                self.comboBox_camada_ltm_hom.addItem(base_config["nome"])

        except Exception as e:
            print(e)

    def add_action_ltm_nao_homologada(self):
        try:
            id_base_selec = self.comboBox_base_ltm_n_hom.currentData()[0]

            base_config = self.search_base_pg(id_base_selec)

            if base_config == {}:
                base_config = self.search_base_shp(id_base_selec)

            if base_config["tipo"] == "pg":
                self.comboBox_camada_ltm_n_hom.clear()
                for item_camada in base_config["tabelasCamadas"]:
                    self.comboBox_camada_ltm_n_hom.addItem(item_camada)

            if base_config["tipo"] == "shp":
                self.comboBox_camada_ltm_n_hom.clear()
                self.comboBox_camada_ltm_n_hom.addItem(base_config["nome"])

        except Exception as e:
            print(e)

    def add_action_area_uniao(self):
        try:
            id_base_selec = self.comboBox_base_area_uniao.currentData()[0]

            base_config = self.search_base_pg(id_base_selec)

            if base_config == {}:
                base_config = self.search_base_shp(id_base_selec)

            if base_config["tipo"] == "pg":
                self.comboBox_camada_area_uniao.clear()
                for item_camada in base_config["tabelasCamadas"]:
                    self.comboBox_camada_area_uniao.addItem(item_camada)

            if base_config["tipo"] == "shp":
                self.comboBox_camada_area_uniao.clear()
                self.comboBox_camada_area_uniao.addItem(base_config["nome"])

        except Exception as e:
            print(e)

    def add_action_area_uniao_n_hom(self):
        try:
            id_base_selec = self.comboBox_base_area_uniao_n_hom.currentData()[0]

            base_config = self.search_base_pg(id_base_selec)

            if base_config == {}:
                base_config = self.search_base_shp(id_base_selec)

            if base_config["tipo"] == "pg":
                self.comboBox_camada_area_uniao_n_hom.clear()
                for item_camada in base_config["tabelasCamadas"]:
                    self.comboBox_camada_area_uniao_n_hom.addItem(item_camada)

            if base_config["tipo"] == "shp":
                self.comboBox_camada_area_uniao_n_hom.clear()
                self.comboBox_camada_area_uniao_n_hom.addItem(base_config["nome"])

        except Exception as e:
            print(e)

    def add_action_lltm_n_hom(self):
        try:
            id_base_selec = self.comboBox_base_lltm_n_hom.currentData()[0]

            base_config = self.search_base_pg(id_base_selec)

            if base_config == {}:
                base_config = self.search_base_shp(id_base_selec)

            if base_config["tipo"] == "pg":
                self.comboBox_camada_lltm_n_hom.clear()
                for item_camada in base_config["tabelasCamadas"]:
                    self.comboBox_camada_lltm_n_hom.addItem(item_camada)

            if base_config["tipo"] == "shp":
                self.comboBox_camada_lltm_n_hom.clear()
                self.comboBox_camada_lltm_n_hom.addItem(base_config["nome"])

        except Exception as e:
            print(e)

    def add_action_lltm_hom(self):
        try:
            id_base_selec = self.comboBox_base_lltm_hom.currentData()[0]

            base_config = self.search_base_pg(id_base_selec)

            if base_config == {}:
                base_config = self.search_base_shp(id_base_selec)

            if base_config["tipo"] == "pg":
                self.comboBox_camada_lltm_hom.clear()
                for item_camada in base_config["tabelasCamadas"]:
                    self.comboBox_camada_lltm_hom.addItem(item_camada)

            if base_config["tipo"] == "shp":
                self.comboBox_camada_lltm_hom.clear()
                self.comboBox_camada_lltm_hom.addItem(base_config["nome"])

        except Exception as e:
            print(e)

    def add_action_lmeo_n_hom(self):
        try:
            id_base_selec = self.comboBox_base_lmeo_n_hom.currentData()[0]

            base_config = self.search_base_pg(id_base_selec)

            if base_config == {}:
                base_config = self.search_base_shp(id_base_selec)

            if base_config["tipo"] == "pg":
                self.comboBox_camada_lmeo_n_hom.clear()
                for item_camada in base_config["tabelasCamadas"]:
                    self.comboBox_camada_lmeo_n_hom.addItem(item_camada)

            if base_config["tipo"] == "shp":
                self.comboBox_camada_lmeo_n_hom.clear()
                self.comboBox_camada_lmeo_n_hom.addItem(base_config["nome"])

        except Exception as e:
            print(e)

    def add_action_lmeo_hom(self):
        try:
            id_base_selec = self.comboBox_base_lmeo_hom.currentData()[0]

            base_config = self.search_base_pg(id_base_selec)

            if base_config == {}:
                base_config = self.search_base_shp(id_base_selec)

            if base_config["tipo"] == "pg":
                self.comboBox_camada_lmeo_hom.clear()
                for item_camada in base_config["tabelasCamadas"]:
                    self.comboBox_camada_lmeo_hom.addItem(item_camada)

            if base_config["tipo"] == "shp":
                self.comboBox_camada_lmeo_hom.clear()
                self.comboBox_camada_lmeo_hom.addItem(base_config["nome"])

        except Exception as e:
            print(e)

    def save_mandatory_layers(self):

        config = {}
        if self.groupBox_area_uniao.isChecked():
            current_base = self.comboBox_base_area_uniao.itemData(self.comboBox_base_area_uniao.currentIndex())[0]
            current_tipo = self.comboBox_base_area_uniao.itemData(self.comboBox_base_area_uniao.currentIndex())[1]
            current_camada = self.comboBox_camada_area_uniao.currentText()
            if current_tipo == 'shp':
                config["area_homologada"] = [current_base, "", "Área Homologada"]
            else:
                config["area_homologada"] = [current_base, current_camada, "Área Homologada"]

        if self.groupBox_lmeo_hom.isChecked():
            current_base = self.comboBox_base_lmeo_hom.itemData(self.comboBox_base_lmeo_hom.currentIndex())[0]
            current_tipo = self.comboBox_base_lmeo_hom.itemData(self.comboBox_base_lmeo_hom.currentIndex())[1]
            current_camada = self.comboBox_camada_lmeo_hom.currentText()

            if current_tipo == 'shp':
                config["lmeo_homologada"] = [current_base, "", "LMEO Homologada"]
            else:
                config["lmeo_homologada"] = [current_base, current_camada, "LMEO Homologada"]

        if self.groupBox_lltm_hom.isChecked():
            current_base = self.comboBox_base_lltm_hom.itemData(self.comboBox_base_lltm_hom.currentIndex())[0]
            current_tipo = self.comboBox_base_lltm_hom.itemData(self.comboBox_base_lltm_hom.currentIndex())[1]
            current_camada = self.comboBox_camada_lltm_hom.currentText()
            if current_tipo == 'shp':
                config["lltm_homologada"] = [current_base, "", "LLTM Homologada"]
            else:
                config["lltm_homologada"] = [current_base, current_camada, "LLTM Homologada"]

        if self.groupBox_lpm_hom.isChecked():
            current_base = self.comboBox_base_lpm_hom.itemData(self.comboBox_base_lpm_hom.currentIndex())[0]
            current_tipo = self.comboBox_base_lpm_hom.itemData(self.comboBox_base_lpm_hom.currentIndex())[1]
            current_camada = self.comboBox_camada_lpm_hom.currentText()
            if current_tipo == 'shp':
                config["lpm_homologada"] = [current_base, "", "LPM Homologada"]
            else:
                config["lpm_homologada"] = [current_base, current_camada, "LPM Homologada"]

        if self.groupBox_ltm_hom.isChecked():
            current_base = self.comboBox_base_ltm_hom.itemData(self.comboBox_base_ltm_hom.currentIndex())[0]
            current_tipo = self.comboBox_base_ltm_hom.itemData(self.comboBox_base_ltm_hom.currentIndex())[1]
            current_camada = self.comboBox_camada_ltm_hom.currentText()
            if current_tipo == 'shp':
                config["ltm_homologada"] = [current_base, "", "LTM Homologada"]
            else:
                config["lpm_homologada"] = [current_base, current_camada, "LPM Homologada"]

        if self.groupBox_area_uniao_n_hom.isChecked():
            current_base = self.comboBox_base_area_uniao_n_hom.itemData(self.comboBox_base_area_uniao_n_hom.currentIndex())[0]
            current_tipo = self.comboBox_base_area_uniao_n_hom.itemData(self.comboBox_base_area_uniao_n_hom.currentIndex())[1]
            current_camada = self.comboBox_camada_area_uniao_n_hom.currentText()
            if current_tipo == 'shp':
                config["area_nao_homologada"] = [current_base, "", "Área Não Homologada"]
            else:
                config["area_nao_homologada"] = [current_base, current_camada, "Área Não Homologada"]

        if self.groupBox_lmeo_n_hom.isChecked():
            current_base = self.comboBox_base_lmeo_n_hom.itemData(self.comboBox_base_lmeo_n_hom.currentIndex())[0]
            current_tipo = self.comboBox_base_lmeo_n_hom.itemData(self.comboBox_base_lmeo_n_hom.currentIndex())[1]
            current_camada = self.comboBox_camada_lmeo_n_hom.currentText()
            if current_tipo == 'shp':
                config["lmeo_nao_homologada"] = [current_base, "", "LMEO Não Homologada"]
            else:
                config["lmeo_nao_homologada"] = [current_base, current_camada, "LMEO Não Homologada"]


        if self.groupBox_lltm_n_hom.isChecked():
            current_base = self.comboBox_base_lltm_n_hom.itemData(self.comboBox_base_lltm_n_hom.currentIndex())[0]
            current_tipo = self.comboBox_base_lltm_n_hom.itemData(self.comboBox_base_lltm_n_hom.currentIndex())[1]
            current_camada = self.comboBox_camada_lltm_n_hom.currentText()
            if current_tipo == 'shp':
                config["lltm_nao_homologada"] = [current_base, "", "LLTM Não Homologada"]
            else:
                config["lltm_nao_homologada"] = [current_base, current_camada, "LLTM Não Homologada"]


        if self.groupBox_lpm_n_hom.isChecked():
            current_base = self.comboBox_base_lpm_n_hom.itemData(self.comboBox_base_lpm_n_hom.currentIndex())[0]
            current_tipo = self.comboBox_base_lpm_n_hom.itemData(self.comboBox_base_lpm_n_hom.currentIndex())[1]
            current_camada = self.comboBox_camada_lpm_n_hom.currentText()
            if current_tipo == 'shp':
                config["lpm_nao_homologada"] = [current_base, "", "LPM Não Homologada"]
            else:
                config["lpm_nao_homologada"] = [current_base, current_camada, "LPM Não Homologada"]


        if self.groupBox_ltm_n_hom.isChecked():
            current_base = self.comboBox_base_ltm_n_hom.itemData(self.comboBox_base_ltm_n_hom.currentIndex())[0]
            current_tipo = self.comboBox_base_ltm_n_hom.itemData(self.comboBox_base_ltm_n_hom.currentIndex())[1]
            current_camada = self.comboBox_camada_ltm_n_hom.currentText()
            if current_tipo == 'shp':
                config["ltm_nao_homologada"] = [current_base, "", "LTM Não Homologada"]
            else:
                config["ltm_nao_homologada"] = [current_base, current_camada, "LTM Não Homologada"]


        self.settings.set_camadas_base_obrigatoria(config)

    def delete_bd(self):
        msg = QMessageBox(self)
        ret = msg.question(self, 'Deletar configuração',
                           "Você realmente deseja excluir a configuracão de " + self.combo_box_shp.currentText() + "?",
                           QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.settings.delete_base(self.combo_box_base.currentData())
            self.nome_base.clear()
            self.host.clear()
            self.porta.clear()
            self.base_de_dados.clear()
            self.orgao_responsavel_base.clear()
            self.textEdit_bd.clear()
            self.usuario.clear()
            self.senha.clear()
            self.combo_box_base.removeItem(self.combo_box_base.currentIndex())
            self.combo_box_base.setCurrentIndex(0)

    def delete_shp(self):
        #self.settings.delete_base(self.combo_box_shp.currentData())
        msg = QMessageBox(self)
        ret = msg.question(self, 'Deletar configuração', "Você realmente deseja excluir a configuração de " + self.combo_box_shp.currentText() +"?", QMessageBox.Yes | QMessageBox.No)

        if ret == QMessageBox.Yes:
            self.settings.delete_base(self.combo_box_shp.currentData())
            self.nome_shp.clear()
            self.url_dowload.clear()
            self.diretorioLocalshp.setFilePath("")
            self.orgao_responsavel_shp.clear()
            self.style_path.setFilePath("")
            self.textEdit_shp.clear()
            self.faixa_proximidade.clear()
            self.combo_box_shp.removeItem(self.combo_box_shp.currentIndex())
            self.combo_box_shp.setCurrentIndex(0)

    def enable_disable_delete_shp(self):
        if self.combo_box_shp.currentIndex() == 0:
            self.delete_sh.setEnabled(False)
        if self.combo_box_shp.currentIndex() != 0:
            self.delete_sh.setEnabled(True)

    def handle_combo_wfs(self):
        if self.combo_wfs.currentIndex() == 0:
            self.btn_delete_wfs.setEnabled(False)

            self.txt_nome_wfs.clear()
            self.txt_link_wfs.clear()
            self.txt_descricao_wfs.clear()
            self.tbl_wfs.setRowCount(0)
            self.combo_wfs.setCurrentIndex(0)

        if self.combo_wfs.currentIndex() != 0:
            self.btn_delete_wfs.setEnabled(True)

    def enable_disable_delete_bd(self):
        if self.combo_box_base.currentIndex() == 0:
            self.delete_base.setEnabled(False)
        if self.combo_box_base.currentIndex() != 0:
            self.delete_base.setEnabled(True)

    def handle_wfs(self):
        self.link_wfs = self.txt_link_wfs.text()

        wfs_operations = WfsOperations()

        self.wfs_data = wfs_operations.get_wfs_informations(self.link_wfs)

        # Configura quantidade de linhas e as colunas da tabela de resultados
        self.tbl_wfs.setColumnCount(8)
        self.tbl_wfs.setRowCount(len(self.wfs_data))
        self.tbl_wfs.setHorizontalHeaderLabels(['Camada', 'Nome Fantasia', "Órgão Responsável", "Periodo de aquisição", "Periodo de referência", "Faixa de proximidade", "Arquivo SLD", "Descrição"])

        self.tbl_wfs.horizontalHeader().setStretchLastSection(True)
        self.tbl_wfs.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        row_control = 0
        for data in self.wfs_data:
            item = QtWidgets.QTableWidgetItem(str(data[1]))
            item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                          QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Unchecked)
            cellName = QtWidgets.QTableWidgetItem(item)
            self.tbl_wfs.setItem(row_control, 0, cellName)

            cellName = QtWidgets.QTableWidgetItem("")
            self.tbl_wfs.setItem(row_control, 1, cellName)

            cellName = QtWidgets.QTableWidgetItem("")
            self.tbl_wfs.setItem(row_control, 2, cellName)

            cellName = QgsDateTimeEdit()
            cellName.setDisplayFormat("dd/MM/yyyy")
            self.tbl_wfs.setCellWidget(row_control, 3, cellName)

            cellName = QgsDateTimeEdit()
            cellName.setDisplayFormat("dd/MM/yyyy")
            self.tbl_wfs.setCellWidget(row_control, 4, cellName)

            cellName = QtWidgets.QTableWidgetItem("0")
            self.tbl_wfs.setItem(row_control, 5, cellName)

            cellName = QgsFileWidget()
            self.tbl_wfs.setCellWidget(row_control, 6, cellName)

            row_control += 1

        self.tbl_wfs.itemClicked.connect(self.handleItemClicked)
        self._list = []

    def fill_data_wfs(self):
        for item in self.source_wfs:
            if item['id'] == self.combo_wfs.currentData():
                self.txt_nome_wfs.setText(item['nome'])
                self.txt_link_wfs.setText(item['link'])
                self.txt_descricao_wfs.setText(item['descricao_base'])

                get_date = item["dataAquisicao"].split("/")
                date = QtCore.QDate(int(get_date[2]), int(get_date[1]), int(get_date[0]))
                self.date_aquisicao_wfs.setDate(date)

                # get_date = item["periodosReferencia"].split("/")
                # date = QtCore.QDate(int(get_date[2]), int(get_date[1]), int(get_date[0]))
                # self.date_referencia_wfs.setDate(date)

                # Configura quantidade de linhas e as colunas da tabela de resultados
                self.tbl_wfs.setColumnCount(9)
                self.tbl_wfs.setRowCount(len(item['tabelasCamadas']))
                self.tbl_wfs.setHorizontalHeaderLabels(
                    ['Camada', 'Nome Fantasia', "Órgão Responsável", "Periodo de aquisição", "Periodo de referência", "Faixa de proximidade",
                     "Arquivo SLD", "Descrição", "Atualizar camada"])

                self.tbl_wfs.horizontalHeader().setStretchLastSection(True)
                self.tbl_wfs.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

                # Lista que controla quais linhas da tabela foram clicadas
                self._list = []

                row_control = 0
                layer_control = 0
                for index, data in enumerate(item['tabelasCamadas']):
                    item_tbl = QtWidgets.QTableWidgetItem(item['tabelasCamadasNomesFantasia'][index])
                    item_tbl.setFlags(QtCore.Qt.ItemIsUserCheckable |
                                  QtCore.Qt.ItemIsEnabled)
                    if item['tabelasCamadasNomesFantasia'][index] in item['wfsSelecionadas']:
                        item_tbl.setCheckState(QtCore.Qt.Checked)
                        self._list.append(int(index))
                    else:
                        item_tbl.setCheckState(QtCore.Qt.Unchecked)
                    cellName = QtWidgets.QTableWidgetItem(item_tbl)
                    self.tbl_wfs.setItem(row_control, 0, cellName)

                    if item['tabelasCamadasNomesFantasia'][index] in item['wfsSelecionadas']:
                        cellName = QtWidgets.QTableWidgetItem(item['nomeFantasiaTabelasCamadas'][layer_control])
                    else:
                        cellName = QtWidgets.QTableWidgetItem("")
                    self.tbl_wfs.setItem(row_control, 1, cellName)

                    if item['tabelasCamadasNomesFantasia'][index] in item['wfsSelecionadas']:
                        cellName = QtWidgets.QTableWidgetItem(item['orgaoResponsavel'][layer_control])
                    else:
                        cellName = QtWidgets.QTableWidgetItem("")
                    self.tbl_wfs.setItem(row_control, 2, cellName)

                    cellName = QgsDateTimeEdit()
                    cellName.setDisplayFormat("dd/MM/yyyy")
                    if item['tabelasCamadasNomesFantasia'][index] in item['wfsSelecionadas']:
                        get_date = item["periodoAquisicao"][layer_control].split("/")
                        date = QtCore.QDate(int(get_date[2]), int(get_date[1]), int(get_date[0]))
                        cellName.setDate(date)
                    self.tbl_wfs.setCellWidget(row_control, 3, cellName)

                    cellName = QgsDateTimeEdit()
                    cellName.setDisplayFormat("dd/MM/yyyy")
                    if item['tabelasCamadasNomesFantasia'][index] in item['wfsSelecionadas']:
                        get_date = item["periodosReferencia"][layer_control].split("/")
                        date = QtCore.QDate(int(get_date[2]), int(get_date[1]), int(get_date[0]))
                        cellName.setDate(date)
                    self.tbl_wfs.setCellWidget(row_control, 4, cellName)

                    if item['tabelasCamadasNomesFantasia'][index] in item['wfsSelecionadas']:
                        cellName = QtWidgets.QTableWidgetItem(str(item['aproximacao'][layer_control]))
                    else:
                        cellName = QtWidgets.QTableWidgetItem("0")
                    self.tbl_wfs.setItem(row_control, 5, cellName)

                    if item['tabelasCamadasNomesFantasia'][index] in item['wfsSelecionadas']:
                        cellName = QgsFileWidget()
                        cellName.setFilePath(item['estiloTabelasCamadas'][layer_control])
                    else:
                        cellName = QgsFileWidget()
                    self.tbl_wfs.setCellWidget(row_control, 6, cellName)

                    if item['tabelasCamadasNomesFantasia'][index] in item['wfsSelecionadas']:
                        cellName = QtWidgets.QTableWidgetItem(item['descricao'][layer_control])
                        layer_control += 1
                    else:
                        cellName = QtWidgets.QTableWidgetItem("")
                    self.tbl_wfs.setItem(row_control, 7, cellName)

                    cellName = QtWidgets.QPushButton('Atualizar', self)
                    cellName.clicked.connect(self.update_wfs_layer)
                    self.tbl_wfs.setCellWidget(row_control, 8, cellName)

                    row_control += 1
                self._list.sort()
                self.tbl_wfs.itemClicked.connect(self.handleItemClicked)

    def update_wfs_layer(self):
        wfs_operations = WfsOperations()
        # self.wfs_data = wfs_operations.get_wfs_informations(self.txt_link_wfs.text())
        row = self.tbl_wfs.currentRow()
        msg = QMessageBox(self)
        ret = msg.question(self, 'Atualizar camada WFS',
                           "Você realmente deseja atualizar a camada " + str(self.tbl_wfs.item(row, 0).text()) + "?",
                           QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            for index, item in enumerate(self.source_wfs):
                if item['id'] == self.combo_wfs.currentData():
                    wfs_operations.update_wfs_layer(self.txt_link_wfs.text(), self.source_wfs[index]['tabelasCamadas'][row], self.source_wfs[index]['nome'])
                    ret = msg.question(self, 'Camada atualizada',
                                       "Camada atualizada com sucesso!",
                                       QMessageBox.Ok)

    def delete_wfs_config(self):
        msg = QMessageBox(self)
        ret = msg.question(self, 'Deletar configuração',
                           "Você realmente deseja excluir a configuracão de " + self.combo_wfs.currentText() + "?",
                           QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.settings.delete_base(self.combo_wfs.currentData())
            self.txt_nome_wfs.clear()
            self.txt_link_wfs.clear()
            self.txt_descricao_wfs.clear()
            self.tbl_wfs.setRowCount(0)
            self.combo_wfs.removeItem(self.combo_wfs.currentIndex())
            self.combo_wfs.setCurrentIndex(0)

    def get_wfs_json(self, id_json):
        json_data = self.settings.get_source_data(id_json)

        zip_lists = zip(json_data.get('tabelasCamadas'), json_data.get('tabelasCamadasNomesFantasia'))
        wfs_data = list(zip_lists)

        return wfs_data

    def save_wfs_config(self):
        if self.tabWidget.currentIndex() != 2:
            return

        if self.txt_nome_wfs == '' or self.txt_link_wfs == '' or self.txt_descricao_wfs == '' or (len(self._list) == 0 and self.combo_wfs.currentIndex() == 0):
            return

        wfs_operations = WfsOperations()

        data = {}
        id_current_wfs: str = ''
        is_update: bool = False
        id_combo = None
        # Significa edição em uma base
        if self.combo_wfs.currentIndex() != 0:
            is_update = True
            id_current_wfs = self.combo_wfs.currentData()
            id_combo = self.combo_wfs.currentIndex()
            self.wfs_data = self.get_wfs_json(id_current_wfs)

        data['nome'] = self.txt_nome_wfs.text()
        data['link'] = self.txt_link_wfs.text()
        data['descricao_base'] = self.txt_descricao_wfs.text()
        data['tipo'] = 'wfs'

        data['nomeFantasiaTabelasCamadas'] = []
        data['diretorio'] = []
        data['orgaoResponsavel'] = []
        data['periodoAquisicao'] = []
        data['periodosReferencia'] = []
        data['aproximacao'] = []
        data['descricao'] = []
        data['estiloTabelasCamadas'] = []

        dt = self.date_aquisicao_wfs.dateTime()
        dt_string = dt.toString(self.date_aquisicao_wfs.displayFormat())
        data['dataAquisicao'] = dt_string

        self._list.sort()

        names_selected_wfs = [self.wfs_data[item][0] for item in self._list]
        data['wfsSelecionadas'] = [self.wfs_data[item][1] for item in self._list]
        data['tabelasCamadas'] = [item[0] for item in self.wfs_data]
        data['tabelasCamadasNomesFantasia'] = [item[1] for item in self.wfs_data]

        for item in self._list:
            layer = self.wfs_data[item][0] \
                .replace(':', '_') \
                .replace('*', '_') \
                .replace('/', '_') \
                .replace('\\', '_')
            file_path = os.path.dirname(__file__) + '/../wfs_layers/' + data['nome'] + '/' + layer + ".geojson"
            if self.wfs_data[item][0] in names_selected_wfs:
                # Faz o download da camada somente se a camada ainda não foi baixada (serve para a edição dos dados da base wfs)
                if not os.path.isfile(file_path):
                    try:
                        wfs_operations.download_wfs_layer(self.txt_link_wfs.text(), self.wfs_data[item][0], data['nome'])
                    except Exception as e:
                        print(e)
                        continue
                data['nomeFantasiaTabelasCamadas'].append(self.tbl_wfs.item(item, 1).text())
                data['diretorio'].append(file_path)
                data['orgaoResponsavel'].append(self.tbl_wfs.item(item, 2).text())

                dt = self.tbl_wfs.cellWidget(item, 3).dateTime()
                dt_string = dt.toString(self.tbl_wfs.cellWidget(item, 3).displayFormat())
                data["periodoAquisicao"].append(dt_string)

                dt = self.tbl_wfs.cellWidget(item, 4).dateTime()
                dt_string = dt.toString(self.tbl_wfs.cellWidget(item, 4).displayFormat())
                data["periodosReferencia"].append(dt_string)

                data['aproximacao'].append(float(self.tbl_wfs.item(item, 5).text()))
                data['estiloTabelasCamadas'].append(self.tbl_wfs.cellWidget(item, 6).filePath())
                data['descricao'].append(self.tbl_wfs.item(item, 7).text())

        if is_update:
            id_base = id_current_wfs
            self.settings.insert_database_pg(data, id_base)
            self.combo_wfs.removeItem(id_combo)
        else:
            self.settings.insert_database_pg(data)

        self.source_wfs = self.settings.get_config_wfs()
        self.combo_wfs.addItem(data["nome"], data["id"])
        self.combo_wfs.setCurrentText(data["nome"])
        self.fill_data_wfs()

    def handleItemClicked(self, item):
        if self.tbl_wfs.item(item.row(), 0).checkState() == QtCore.Qt.Checked:
            if item.row() not in self._list:
                self._list.append(item.row())
        else:
            if item.row() in self._list:
                self._list.remove(item.row())
                print(self._list)

    def store_path_json(self):
        path = self.path_json.filePath()
        self.credencials.store_path_json(path)


    def fill_path_json(self):
        path = self.credencials.get_path_json()
        self.path_json.setFilePath(str(path))

    def path_mudou(self):
        self.path_json_mudou_flag = 1

    def handle_tabwidget(self, index):
        """
            função para tratar signal de click no TabWidget
        """
        if index == 3:
            self.config_col_tab()

    def config_col_tab(self):
        self.tbl_col_shp.setRowCount(len(self.source_shp))

        for idx, shp in enumerate(self.source_shp):
            nome = shp['nomeFantasiaCamada']
            caminho = shp['diretorioLocal']

            layer = QgsVectorLayer(caminho, f"{nome}",  "ogr")

            field_names = [field.name() for field in layer.fields()] 
            self.cmb_shp_fields1 = comboColunas(self.tbl_col_shp, field_names)
            self.cmb_shp_fields2 = comboColunas(self.tbl_col_shp, field_names)
            self.cmb_shp_fields3 = comboColunas(self.tbl_col_shp, field_names)

            qitem_nome = QTableWidgetItem(nome)

            self.tbl_col_shp.setItem(idx, 0, qitem_nome)
            self.tbl_col_shp.setCellWidget(idx, 1, self.cmb_shp_fields1)
            self.tbl_col_shp.setCellWidget(idx, 2, self.cmb_shp_fields2)
            self.tbl_col_shp.setCellWidget(idx, 3, self.cmb_shp_fields3)

        et = EnvTools()
        for i in self.source_databases:
            user, pwd = et.get_credentials(i['id'])

            port = i['porta']
            host = i['host']
            dbase = i['baseDeDados']
            nomes = i['nomeFantasiaTabelasCamadas']

            self.tbl_col_bd.setRowCount(len(nomes))

            uri = QgsDataSourceUri()
            uri.setConnection(host, port, dbase, user, pwd)

            for idx, camada in enumerate(i['tabelasCamadas']):
                uri.setDataSource('public', f'{camada}', 'geom')
                layer = QgsVectorLayer(uri.uri(False), camada, 'postgres')
                field_names = [field.name() for field in layer.fields()]
                self.cmb_db_fields1 = comboColunas(
                    self.tbl_col_bd, field_names)
                self.cmb_db_fields2 = comboColunas(
                    self.tbl_col_bd, field_names)
                self.cmb_db_fields3 = comboColunas(
                    self.tbl_col_bd, field_names)

                qitem_nome = QTableWidgetItem(nomes[idx])

                self.tbl_col_bd.setItem(idx, 0, qitem_nome)
                self.tbl_col_bd.setCellWidget(idx, 1, self.cmb_db_fields1)
                self.tbl_col_bd.setCellWidget(idx, 2, self.cmb_db_fields2)
                self.tbl_col_bd.setCellWidget(idx, 3, self.cmb_db_fields3)
        
        for wfs in range(len(self.source_wfs)):
            for idx_wfs_layer in range(len(self.source_wfs[wfs]['nomeFantasiaTabelasCamadas'])):
                nome = self.source_wfs[wfs]['nomeFantasiaTabelasCamadas'][idx_wfs_layer]
                geojson = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                'wfs_layers', self.source_wfs[wfs]['nome'],
                self.source_wfs[wfs]['diretorio'][idx_wfs_layer].split(r"/")[-1])
        
                self.tbl_col_wfs.setRowCount(len(self.source_wfs[wfs]['nomeFantasiaTabelasCamadas']))
                
                layer = QgsVectorLayer(geojson, "wfs",  "ogr")
                field_names = [field.name() for field in layer.fields()]

                self.cmb_wfs_fields1 = comboColunas(self.tbl_col_wfs, field_names)
                self.cmb_wfs_fields2 = comboColunas(self.tbl_col_wfs, field_names)
                self.cmb_wfs_fields3 = comboColunas(self.tbl_col_wfs, field_names)

                qitem_nome = QTableWidgetItem(nome)

                self.tbl_col_wfs.setItem(idx_wfs_layer, 0, qitem_nome)
                self.tbl_col_wfs.setCellWidget(idx_wfs_layer, 1, self.cmb_wfs_fields1)
                self.tbl_col_wfs.setCellWidget(idx_wfs_layer, 2, self.cmb_wfs_fields2)
                self.tbl_col_wfs.setCellWidget(idx_wfs_layer, 3, self.cmb_wfs_fields3)

            
class comboColunas(QComboBox):
    def __init__(self, parent, lista_itens):
        super().__init__(parent)
        self.addItems(lista_itens)
        self.setCurrentIndex(-1)

