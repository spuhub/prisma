import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

from .json_tools import JsonTools

class LayerInfor(QtWidgets.QDialog):
    """
    Classe responsável por manipular a janela de configuração de informações adicionais de camadas.

    Essa classe permite exibir, editar e salvar informações adicionais das camadas de uma base de dados específica.

    Atributos:
        back_window (QtCore.pyqtSignal): Sinal emitido ao retornar para a janela anterior.
        continue_window (QtCore.pyqtSignal): Sinal emitido ao continuar para a próxima janela.
        id_current_db (str): ID da base de dados atualmente sendo configurada.
        index_infor (int): Índice da camada dentro das informações adicionais.
        settings (JsonTools): Instância para manipulação do arquivo JSON de configuração.
        source_databases (list): Lista das configurações de bases disponíveis no JSON.
    """

    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self, id_current_db, index_infor):
        """
        Inicializa a janela de configuração de informações adicionais.

        Args:
            id_current_db (str): ID da base de dados atualmente sendo configurada.
            index_infor (int): Índice da camada para edição das informações adicionais.
        """
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
        """
        Busca as configurações de uma base de dados PostgreSQL no JSON de configuração.

        Args:
            id_base (str): ID da base de dados.

        Returns:
            dict: Configurações da base de dados correspondente.
        """
        config = {}
        for item in self.source_databases:
            if item["id"] == id_base:
                config = item

        return config

    def fill_itens_infor(self):
        """
        Preenche os campos da interface com as informações adicionais da camada selecionada.

        Caso a camada possua informações previamente configuradas, essas são exibidas nos campos da interface.
        """
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
        """
        Salva as informações adicionais configuradas para a camada no arquivo JSON.

        Atualiza ou cria as informações adicionais da camada no JSON, incluindo dados como órgão responsável, 
        período de referência, data de aquisição e descrição.

        Após salvar, emite o sinal `continue_window` para prosseguir.
        """
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
        """
        Retorna o estado atual das configurações da base de dados.

        Returns:
            dict: Configurações atuais da base de dados selecionada.
        """
        config = self.search_base_pg(self.id_current_db)
        return config
