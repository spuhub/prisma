import json
import sys
import os.path

import geopandas as gpd

from qgis.PyQt.QtWidgets import QAction, QFileDialog

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi
from ..settings.env_tools import EnvTools


# from ..dbtools.shp_tools import ShpTools

class ReportGenerator(QtWidgets.QDialog):
    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal(dict)

    def __init__(self):
        # self.iface = iface
        super(ReportGenerator, self).__init__()
        self.envtools = EnvTools()
        loadUi(os.path.join(os.path.dirname(__file__), 'report_generator.ui'), self)
        self.fill_fields()
        self.buttonBox.accepted.connect(self.report_generator)
        #self.buttonBox.rejected.connect(self.envtools.clear_repor_header)

    def save_fields(self):
        field = {"ministerio": self.ministerio.text(),
                 "secretariaEspecial": self.secretariaEspecial.text(),
                 "secretaria": self.secretaria.text(),
                 "superintendencia": self.superintendencia.text(),
                 "setor": self.setor.text()}

        self.envtools.store_report_hearder(field)

    def fill_fields(self):
        print(self.envtools.get_report_hearder())
        field = self.envtools.get_report_hearder()
        if "ministerio" in field:
            self.ministerio.setText(field["ministerio"])
        if "secretariaEspecial" in field:
            self.secretariaEspecial.setText(field["secretariaEspecial"])
        if "secretaria" in field:
            self.secretaria.setText(field["secretaria"])
        if "superintendencia" in field:
            self.superintendencia.setText(field["superintendencia"])
        if "setor" in field:
            self.setor.setText(field["setor"])

    def report_generator(self):
        self.save_fields()



        # inserir aqui os outros codigos.
