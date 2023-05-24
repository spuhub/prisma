import os.path

from qgis.core import QgsFeature, QgsVectorLayer, QgsGeometry,  QgsPointXY, QgsCoordinateReferenceSystem, QgsProject
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.uic import loadUi

import PyPDF2
import os, re


class MemorialConversion (QtWidgets.QDialog):
    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal(dict)

    def __init__(self, iface):
        """Método construtor da classe."""
        self.iface = iface
        super(MemorialConversion, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'memorial_conversion.ui'), self)

        self.select_crs.setCrs(QgsCoordinateReferenceSystem('EPSG:4326'))
        self.btn_voltar.clicked.connect(self.back)
        self.btn_input.clicked.connect(self.handle_input)
        self.btn_continuar.clicked.connect(self.next)

    def handle_input(self):
        """
        Exibe uma janela para o usuário selecionar o arquivo PDF de entrada
        """
        self.path_shp_input = QFileDialog.getOpenFileName(self, "Selecione um arquivo PDF de entrada", '*.pdf')[0]
        self.txt_input.setText(self.path_shp_input)
        return self.path_shp_input

    def back(self):
        """
        Retorna para tela anterior.
        """
        self.hide()

    def next(self):
        """
        Faz operações necessárias para extrair as coordenadas do PDF e gerar a geometria.
        """
        self.path_input = self.txt_input.text()
        self.ex_coords = self.txt_example_coords.text()

        # Testa se o diretório do pdf de entrada foi inserido
        if (self.path_input != ""):
            
            lista_coords = self.extrai_coords(self.path_input)
            lyr_pdf = self.gerar_layer(lista_coords)

            self.hide()

        else:
            self.iface.messageBar().pushMessage("Error", "Selecione um pdf de entrada.", level=1)

    def extrai_coords(self, arq_pdf):
        """
            Função que extrai coordenadas de pdf's usando REGEX
        """
        pdfFileObj = open(arq_pdf,'rb')

        pdf_reader = PyPDF2.PdfFileReader(pdfFileObj)
        totalPages = pdf_reader.numPages
        text_out = ""
        regex_str = self.get_regex_from_str(self.ex_coords)

        for i in range(0, totalPages):
            pages = pdf_reader.getPage(i)
            text = pages.extractText()
            text_out += text

        lista_coords = re.findall(regex_str, text_out)


        return lista_coords
    
    def gerar_layer(self, lista):
        """
            Função para geração de layer de geometria extraida, a partir de coordenadas
        """
        mem_layer = QgsVectorLayer(f"Polygon?crs={self.select_crs.crs().authid().lower()}", "Memorial Descritivo - PDF", "Memory")
        QgsProject.instance().addMapLayer(mem_layer)
        poly_coords = []

        for idx, coords in enumerate(lista):
            latitude = float(coords.split(', ')[1].replace(".", "").replace("N ", "").replace(",","."))
            longitude = float(coords.split(', ')[0].replace(".", "").replace("E ", "").replace(",","."))
            poly_coords.append((longitude, latitude))

        polygon = QgsGeometry.fromPolygonXY( [[ QgsPointXY( pair[0], pair[1] ) for pair in poly_coords ]])
        feature = QgsFeature()
        feature.setGeometry(polygon)
        mem_layer.dataProvider().addFeatures([feature])

        return mem_layer

    def get_regex_from_str(self, string):
        """
            Função que extrai padrão REGEX a partir de par de coordenada passado como exemplo
        """
        str_return = ""
        for character in string:
            if character.isdigit():
                str_return += '\d'
            elif character.isspace():
                str_return += '\s'
            else:
                str_return += character
        return str_return
            