import os.path

from qgis.core import QgsVectorLayer

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.uic import loadUi

class OverlayShapefile (QtWidgets.QDialog):
    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal(dict)

    def __init__(self, iface):
        """Método construtor da classe."""
        self.iface = iface
        super(OverlayShapefile, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'overlay_shapefile.ui'), self)

        self.btn_voltar.clicked.connect(self.back)
        self.btn_input.clicked.connect(self.handle_input)
        self.btn_continuar.clicked.connect(self.next)

    def handle_input(self):
        """
        Exibe uma janela para o usuário selecionar o arquivo shapefile de entrada
        """
        self.path_shp_input = QFileDialog.getOpenFileName(self, "Selecione um arquivo SHP de entrada", '*.shp')[0]
        self.txt_input.setText(self.path_shp_input)
        return self.path_shp_input

    def back(self):
        """
        Retorna para tela anterior.
        """
        self.hide()

    def next(self):
        """
        Faz operações necessárias para iniciar o processo de busca de sobreposição através de um shapefile como input.
        """
        self.path_input = self.txt_input.text()
        # Testa se o diretório do shp de entrada foi inserido
        if (self.path_input != ""):
            # Testa se o shp de entrada possui os campos obrigatórios
            lyr_input = QgsVectorLayer(self.path_input, 'Input', 'ogr')
            fields = [field.name() for field in lyr_input.fields()]
            
            if 'cpf_cnpj' and 'logradouro' in fields:
                self.hide()
                data = {'operation': 'shapefile', 'input': {'layer': lyr_input}}

                # Caso usuário tenha inserido área de aproximação
                text_aproximacao = self.txt_aproximacao.text()

                if text_aproximacao.replace(".", '', 1).replace(",", '', 1).isnumeric():
                    if text_aproximacao != '' and float(self.txt_aproximacao.text()) > 0 :
                        data['input'].update(aproximacao = float(self.txt_aproximacao.text()))

                self.continue_window.emit(data)
            else:
                self.iface.messageBar().pushMessage("Error", "O shapefile de entrada não possui os dados de entrada obrigatórios.", level=1)

        else:
            self.iface.messageBar().pushMessage("Error", "Selecione um shapefile de entrada.", level=1)
