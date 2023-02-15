import os.path
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
from ..settings.env_tools import EnvTools

from ..qgis.layout_manager import LayoutManager


# from ..dbtools.shp_tools import ShpTools

class ReportGenerator(QtWidgets.QDialog):
    def __init__(self, data):
        self.data = data
        self.path_output = ""
        super(ReportGenerator, self).__init__()
        self.envtools = EnvTools()
        loadUi(os.path.join(os.path.dirname(__file__), 'report_generator.ui'), self)
        self.fill_fields()
        
        self.btn_output.clicked.connect(self.handle_output)

        self.progress_bar.setHidden(True)
        self.label_process.setHidden(True)

        self.btn_continuar.clicked.connect(self.next)

    def save_fields(self):
        field = {"ministerio": self.ministerio.text(),
                 "secretariaEspecial": self.secretariaEspecial.text(),
                 "secretaria": self.secretaria.text(),
                 "superintendencia": self.superintendencia.text(),
                 "setor": self.setor.text()}

        self.envtools.store_report_hearder(field)

    def fill_fields(self):
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


    def hidden_fields(self):
        self.label.setHidden(True)
        self.label_2.setHidden(True)
        self.label_3.setHidden(True)
        self.label_4.setHidden(True)
        self.label_5.setHidden(True)
        self.label_6.setHidden(True)
        self.ministerio.setHidden(True)
        self.secretariaEspecial.setHidden(True)
        self.secretaria.setHidden(True)
        self.superintendencia.setHidden(True)
        self.setor.setHidden(True)

        self.label_process.setHidden(False)

    def handle_output(self):
        self.path_output = QFileDialog.getExistingDirectory(self, "Selecione a pasta de saída")
        self.line_output.setText(self.path_output)
        return self.path_output

    def next(self):
        self.save_fields()
        self.hidden_fields()

        self.data['path_output'] = self.path_output

        self.btn_voltar.setHidden(True)
        self.btn_continuar.setHidden(True)

        lm = LayoutManager(self.data, self.progress_bar)
        lm.pdf_generator()

        self.hide()