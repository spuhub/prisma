import sys
import os.path

from qgis.PyQt.QtWidgets import QAction, QFileDialog

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

import geopandas as gpd

class OutputWindow (QtWidgets.QDialog):
    cancel_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self, result):
        self.result = result
        super(OutputWindow, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'output_window.ui'), self)

        self.btn_output.clicked.connect(self.handle_output)
        self.btn_cancel.clicked.connect(self.cancel)
        self.btn_continuar.clicked.connect(self.next)

        self.show_result()

    def show_result(self):
        if(self.result['operation'] == 'shapefile'):
            gdf_result = gpd.GeoDataFrame.from_dict(self.result['gdf'])
            show_result = gdf_result.query('sobreposicao == True').reset_index()

            self.tbl_result.setColumnCount(len(show_result.columns))
            self.tbl_result.setRowCount(len(show_result))
            header_labels = show_result.columns

            self.tbl_result.setHorizontalHeaderLabels(header_labels)
            for rowIndex, row in show_result.iterrows():  # iterando sobre linhas
                columnIndex = 0
                for columnName, value in row.items():   # iterando sobre colunas
                        cell = QtWidgets.QTableWidgetItem(str(value))
                        self.tbl_result.setItem(rowIndex, columnIndex, cell)
                        columnIndex += 1

    def handle_output(self):
        self.output = QFileDialog.getExistingDirectory(self, "Selecione a pasta de saída")
        self.txt_output.setText(self.output)

    def cancel(self):
        self.hide()
        self.cancel_window.emit()

    def next(self):
        self.hide()
        self.continue_window.emit()