import sys
import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QComboBox, QDoubleSpinBox
from PyQt5.uic import loadUi
from qgis.gui import QgsSymbolButton, QgsColorButton
from ..databases.db_connection import DbConnection
from ..databases.shp_handle import ShpHandle


class ConfigLayers(QtWidgets.QDialog):
    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self, tipo_fonte, id_current_db):
        super(ConfigLayers, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'config_layers.ui'), self)
        self.tipoFonte = tipo_fonte
        self.id_current_db = id_current_db
        self.fill_table()

        self.tipo_camada_base_objects = []
        self.estilo_linhas_objects = []
        self.cor_linhas_objects = []
        self.espessura_linhas_objects = []
        self.preenchimento_objects = []
        self.cor_preenchimento_objects = []

        self.btn_layer_cancelar.clicked.connect(self.back)
        self.btn_layer_salvar.clicked.connect(self.next)

    def fill_table(self):
        if self.tipoFonte == "shp":
            self.fill_table_shp()
        if self.tipoFonte == "bd":
            self.fill_table_bd()

    def create_combobox_line_style(self, id_object):
        cb = QComboBox()
        cb.setObjectName(id_object)
        cb.addItem("________________________", "solid")
        cb.addItem("-..-..-..-..-..-..-..-..", "dash dot dot")
        cb.addItem("__.__.__.__.__.__.__.__", "dash dot")
        cb.addItem(".......................", "dot")
        cb.addItem("-----------------------", "dash")
        return cb

    def create_comboBox_tipo_camada_base(self, id_object):
        cb = QComboBox()
        cb.setObjectName(id_object)
        cb.addItem("LPM Homologada","lpm_homologada")
        cb.addItem("LTM Homologada","ltm_homologada")
        cb.addItem("LPM Não Homologada", "lpm_nao_homologada")
        cb.addItem("LTM Não Homologada", "ltm_nao_homologada")
        cb.addItem("Área da União - Homologada", "area_homologada")
        cb.addItem("Área da União - Não Homologada", "area_nao_homologada")
        return cb

    def create_espessura_box(self, id_object):
        dsb = QDoubleSpinBox()
        dsb.setObjectName(id_object)
        dsb.setSingleStep(0.1)
        return dsb

    def create_ComboBox_preenchimento(self,id_object):
        cb = QComboBox()
        cb.setObjectName(id_object)
        cb.addItem("solid", "solid")


    def create_Color_Select(self, id_object):
        co = QgsColorButton()
        co.setObjectName(id_object)
        return co

    def fill_table_shp(self):
        print("shp")

    def fill_table_bd(self):
        print("bd")
        nb_row = 1
        self.table_layers.setRowCount(nb_row)
        # itemCellClass = QTableWidgetItem(classe)
        self.bt = QgsColorButton()
        self.bt.setObjectName("testefill")
        self.table_layers.setCellWidget(0, 4, self.bt)
        self.bt2 = QgsSymbolButton()
        self.bt2.setObjectName("testefill2")
        self.table_layers.setCellWidget(0, 5, self.bt2)
        self.bt3 = QgsSymbolButton()
        self.bt3.setObjectName("testefill3")
        self.table_layers.setCellWidget(0, 7, self.bt3)
        self.bt4 = QgsSymbolButton()
        self.bt4.setObjectName("testefill4")
        self.table_layers.setCellWidget(0, 8, self.bt4)
        self.table_layers.setCellWidget(0,9,self.create_combobox_line_style("cb" + str(0) + str(9)))

        self.table_layers.itemClicked.connect(self.pr)

    def back(self):
        self.hide()
        self.back_window.emit()

    def next(self):
        #print(self.testefill.symbol)
        print(self.bt.color().name())
        self.hide()
        self.continue_window.emit()

    def pr(self):
        print(self.testefill.symbol)
