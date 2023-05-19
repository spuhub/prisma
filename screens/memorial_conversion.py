import os.path

from qgis.core import QgsVectorLayer, QgsCoordinateReferenceSystem

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.uic import loadUi

import PyPDF2
import os, re
from osgeo import ogr


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

        else:
            self.iface.messageBar().pushMessage("Error", "Selecione um pdf de entrada.", level=1)

    def extrai_coords(self, arq_pdf):
        pdfFileObj = open(arq_pdf,'rb')

        pdf_reader = PyPDF2.PdfFileReader(pdfFileObj)
        totalPages = pdf_reader.numPages
        text_out = ""

        for i in range(0, totalPages):
            pages = pdf_reader.getPage(i)
            text = pages.extractText()
            text_out += text

        lista_coords = re.findall(r'E\s\d\d\d\.\d\d\d,\d\d,\sN \d\.\d\d\d\.\d\d\d,\d\d', text_out)

        return lista_coords
    
    def gerar_geom(self, lista):
        ring = ogr.Geometry(ogr.wkbLinearRing)
        poly = ogr.Geometry(ogr.wkbPolygon)

        for idx, coords in enumerate(lista):
            latitude = float(coords.split(', ')[1].replace(".", "").replace("N ", "").replace(",","."))
            longitude = float(coords.split(', ')[0].replace(".", "").replace("E ", "").replace(",","."))
            ring.AddPoint(longitude, latitude)

        poly.AddGeometry(ring)
        
