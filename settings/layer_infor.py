import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

#from .config_layers import ConfigLayers
#from .json_tools import JsonTools
#from .env_tools import EnvTools
from PyQt5.QtWidgets import QMessageBox
from .json_tools import JsonTools
from .env_tools import EnvTools

from ..screens.report_generator import ReportGenerator
from ..databases.db_connection import DbConnection


class LayerInfor(QtWidgets.QDialog):
    """Classe reponsavel por manipular a janela de configuração principal"""

    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self, id_current_db, index_infor):
        super(LayerInfor, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'layer_infor.ui'), self)
        self.btn_salvar.clicked.connect(self.save_infor)
        self.btn_cancelar.clicked.connect(self.back)
        self.id_current_db = id_current_db
        self.index_infor = index_infor

        # self.config_windows = ConfigWindow()
        self.setings = JsonTools()
        self.source_databases = self.setings.get_config_database()
        self.fill_itens_infor()


    def search_base_pg(self, id_base):
        config = {}
        for item in self.source_databases:
            if item["id"] == id_base:
                config = item

        return config

    def fill_itens_infor(self):
        idbd = self.id_current_db
        config = self.search_base_pg(self.id_current_db)
        infor = {}
        if "maisInformacoesTabelas" in config:
            infor = config["maisInformacoesTabelas"]

            if self.index_infor != -1:
                if infor[self.index_infor] != {}:
                    self.orgao_responsavel_base.setText(infor[self.index_infor]["orgaoResponsavel"])

                    get_date = infor[self.index_infor]["periodosReferencia"].split("/")
                    date = QtCore.QDate(int(get_date[2]), int(get_date[1]), int(get_date[0]))
                    self.periodos_referencia_base.setDate(date)

                    get_date = infor[self.index_infor]["dataAquisicao"].split("/")
                    date = QtCore.QDate(int(get_date[2]), int(get_date[1]), int(get_date[0]))
                    self.data_aquisicao_base.setDate(date)

                    self.descricao.setText(infor[self.index_infor]["descricao"])

    def save_infor(self):

        config = self.search_base_pg(self.id_current_db)

        infor_array = []

        if "maisInformacoesTabelas" in config:
            infor_array = config["maisInformacoesTabelas"]
        else:
            for i in range(len(config["tabelasCamadas"])):
                infor_array.append({})


        infor_obj = {}

        infor_obj["orgaoResponsavel"] = self.orgao_responsavel_base.text()

        dt = self.periodos_referencia_base.dateTime()
        dt_string = dt.toString(self.periodos_referencia_base.displayFormat())
        infor_obj["periodosReferencia"] = dt_string

        dt = self.data_aquisicao_base.dateTime()
        dt_string = dt.toString(self.data_aquisicao_base.displayFormat())

        infor_obj["dataAquisicao"] = dt_string
        infor_obj["descricao"] = self.descricao.toPlainText()

        infor_array[self.index_infor] = infor_obj

        config["maisInformacoesTabelas"] = infor_array

        self.setings.edit_database(self.id_current_db, config)
        self.hide()
        self.continue_window.emit()
        #return self.search_base_pg(self.id_current_db)

    def back(self):
        self.hide()
        self.continue_window.emit()

    def get_current_state(self):
        config = self.search_base_pg(self.id_current_db)
        return config
