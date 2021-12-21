import sys
import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.uic import loadUi
from qgis.gui import QgsSymbolButton




class ConfigLayers (QtWidgets.QDialog):

    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self):
        super(ConfigLayers, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'config_layers.ui'), self)

        self.fill_table()
        self.btn_layer_cancelar.clicked.connect(self.back)
        self.btn_layer_salvar.clicked.connect(self.next)


    def fill_table(self):
        nb_row = 1
        self.table_layers.setRowCount(nb_row)
        #itemCellClass = QTableWidgetItem(classe)
        self.bt = QgsSymbolButton()
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



        self.table_layers.itemClicked.connect(self.pr)


    def back(self):
        self.hide()
        self.back_window.emit()


    def next(self):
        print(self.testefill.symbol)
        self.hide()
        self.continue_window.emit()

    def pr(self):
        print(self.testefill.symbol)
