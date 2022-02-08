import os

from qgis.core import QgsProject

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.uic import loadUi

from ..settings.json_tools import JsonTools
from ..analysis.overlay_analysis import OverlayAnalisys
from ..controllers.operation_controller import OperationController

class SelectDatabases(QtWidgets.QDialog):
    cancel_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal(dict)

    def __init__(self, operation_config):
        self.operation_config = operation_config
        self.json_tools = JsonTools()
        self.data_bd = self.json_tools.get_config_database()
        self.data_shp = self.json_tools.get_config_shapefile()

        super(SelectDatabases, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'select_databases.ui'), self)

        # Funcionalidades dos botões da tela
        self.check_bd.clicked.connect(self.handle_check_bd)
        self.check_shp.clicked.connect(self.handle_check_shp)
        self.btn_cancel.clicked.connect(self.cancel)
        self.btn_continuar.clicked.connect(self.next)

        self.load_lists()

    # Adição de checkbox e estilização na lista de shapefiles e bancos de dados
    def load_lists(self):
        for i in range(len(self.data_shp)):
            item = QtWidgets.QListWidgetItem(self.data_shp[i]['nome'])
            item.setFont(QFont('Arial', 10))
            item.setSizeHint(QtCore.QSize(20, 30))
            item.setFlags(item.flags())
            self.list_shp.addItem(item)

        for i in range(len(self.data_bd)):
            item = QtWidgets.QListWidgetItem(self.data_bd[i]['nome'])
            item.setFont(QFont('Arial', 10))
            item.setSizeHint(QtCore.QSize(20, 30))
            item.setFlags(item.flags())
            self.list_bd.addItem(item)

    def handle_check_bd(self):
        if self.check_bd.isChecked():
            self.list_bd.setEnabled(True)
        else:
            self.list_bd.setEnabled(False)

    def handle_check_shp(self):
        if self.check_shp.isChecked():
            self.list_shp.setEnabled(True)
        else:
            self.list_shp.setEnabled(False)

    def load_project(self):
        project = QgsProject.instance()
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(BASE_DIR)
        project.read(BASE_DIR + '/qgis/layouts/SPU-PRISMA_2.0_atlas.qgz')

    def cancel(self):
        self.hide()
        self.cancel_window.emit()

    def next(self):
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

        # Teste de sobreposição
        overlay_analysis = OverlayAnalisys()
        gdf_result = overlay_analysis.OverlayAnalisys(self.operation_config)

        data = {'overlay_shp': gdf_result['overlay_shp'], 'overlay_db': gdf_result['overlay_db'],
                  'input': gdf_result['input'], 'input_standard': gdf_result['input_standard'],
                  'gdf_selected_shp': gdf_result['gdf_selected_shp'], 'gdf_selected_db': gdf_result['gdf_selected_db'],
                  'operation_config': self.operation_config}

        self.continue_window.emit(data)