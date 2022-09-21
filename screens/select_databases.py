import os

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.uic import loadUi

from ..settings.json_tools import JsonTools
from ..utils.data_processing import DataProcessing
from ..analysis.overlay_analysis import OverlayAnalisys
from ..controllers.operation_controller import OperationController


class SelectDatabases(QtWidgets.QDialog):
    """
    Classe responsável por fazer o back-end da tela onde o usuário seleciona as bases de dados.
    A partir dela, duas funções são chamadas: função da classe OperationController, que serve para montar um dicionário contendo as configurações da busca configurada pelo usuário,
    e a função da classe OverlayAnalisys, que em geral, serve para contar quantas sobreposições aconteceram com cada camada e também eliminar áreas de comparação que estão distântes das feições de input.
    """
    cancel_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal(dict)

    def __init__(self, operation_config):
        """
        Inicialização da classe.
        """
        self.operation_config = operation_config
        self.data_processing = DataProcessing()
        self.json_tools = JsonTools()
        self.data_bd = self.json_tools.get_config_database()
        self.data_shp = self.json_tools.get_config_shapefile()
        self.json = self.json_tools.get_json()

        super(SelectDatabases, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'select_databases.ui'), self)

        # Funcionalidades dos botões da tela
        self.check_bd.clicked.connect(self.handle_check_bd)
        self.check_shp.clicked.connect(self.handle_check_shp)
        self.btn_cancel.clicked.connect(self.cancel)
        self.btn_continuar.clicked.connect(self.next)

        self.load_lists()

    def load_lists(self):
        """
        Adição de checkbox e estilização na lista de shapefiles e bancos de dados
        """
        required_shp = []
        required_pg = []

        for key, data in self.json['obrigatorio'].items():
            if data[1] == '':
                required_shp.append(data)
            else:
                required_pg.append(data)

        for i in range(len(self.data_shp)):
            is_required = False
            for x in required_shp:
                if x[0] == self.data_shp[i]['id']:
                    is_required = True

            if is_required == False:
                item = QtWidgets.QListWidgetItem(self.data_shp[i]['nome'])
                item.setFont(QFont('Arial', 10))
                item.setSizeHint(QtCore.QSize(20, 30))
                item.setFlags(item.flags())
                self.list_shp.addItem(item)

        for db in range(len(self.data_bd)):
            for db_layers in range(len(self.data_bd[db]['nomeFantasiaTabelasCamadas'])):
                is_required = False
                for x in required_pg:
                    if x[0] == self.data_bd[db]['id'] and x[1] == self.data_bd[db]['tabelasCamadas'][db_layers]:
                        is_required = True

                if is_required == False:
                    item = QtWidgets.QListWidgetItem(
                        self.data_bd[db]['nomeFantasiaTabelasCamadas'][db_layers] + ' (' + self.data_bd[db]['nome'] + ')')
                    item.setFont(QFont('Arial', 10))
                    item.setSizeHint(QtCore.QSize(20, 30))
                    item.setFlags(item.flags())
                    self.list_bd.addItem(item)

    def handle_check_bd(self):
        """
        Habilita/desabilita tabela contendo base de dados de banco de dados
        """
        if self.check_bd.isChecked():
            self.list_bd.setEnabled(True)
        else:
            self.list_bd.setEnabled(False)

    def handle_check_shp(self):
        """
        Habilita/desabilita tabela contendo base de dados de shapefiles
        """
        if self.check_shp.isChecked():
            self.list_shp.setEnabled(True)
        else:
            self.list_shp.setEnabled(False)

    def cancel(self):
        """
        Retorna para tela anterior.
        """
        self.hide()

    def next(self):
        """
        Faz os tratamentos necessários para executar a busca de sobreposição: Verifica quais bases de comparação foram selecionadas
        e as adiciona em vetores, cria um dicionário identificando que operação vai ser realizada e com quais bases de dados (OperationController),
        faz busca de sobreposição para ver quantas feições se sobrepuseram e envia para tela de resultados um dicionário contendo camadas de input e comparação,
        camadas sobrepostas, configuração da operação, etc..
        """
        self.hide()

        selected_items_shp = []
        selected_items_bd = []

        # Armazena bases de dados selecionadas
        if self.check_shp.isChecked():
            selected_items_shp = [item.text() for item in self.list_shp.selectedItems()]
        if self.check_bd.isChecked():
            selected_items_bd = [item.text() for item in self.list_bd.selectedItems()]

        # Prepara operação que será realizada em formato dicionário
        oc = OperationController()
        self.operation_config = oc.get_operation(self.operation_config, selected_items_shp, selected_items_bd)

        # Leitura e manipulação dos dados
        input, input_standard, gdf_selected_shp, gdf_selected_shp_standard, gdf_selected_db, self.operation_config = self.data_processing.data_preprocessing(
            self.operation_config)

        # Teste de sobreposição
        overlay_analysis = OverlayAnalisys()
        gdf_result = overlay_analysis.overlay_analysis(input, input_standard, gdf_selected_shp, gdf_selected_db, self.operation_config)

        data = {'input': gdf_result['input'], 'input_standard': gdf_result['input_standard'],
                  'gdf_selected_shp': gdf_result['gdf_selected_shp'], 'gdf_selected_shp_standard': gdf_selected_shp_standard,
                  'gdf_selected_db': gdf_result['gdf_selected_db'], 'operation_config': self.operation_config}

        self.continue_window.emit(data)