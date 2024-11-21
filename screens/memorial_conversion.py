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
        self.rdbtn_pdf.setChecked(True)
        self.handle_radios()

        self.btn_voltar.clicked.connect(self.back)
        self.btn_input.clicked.connect(self.handle_input)
        self.btn_continuar.clicked.connect(self.next)
        self.rdbtn_pdf.toggled.connect(self.handle_radios)
        

    def handle_input(self):
        """
        Exibe uma janela para o usuário selecionar o arquivo PDF de entrada
        """
        self.path_shp_input = QFileDialog.getOpenFileName(self, "Selecione um arquivo PDF de entrada", '*.pdf')[0]
        self.txt_input.setText(self.path_shp_input)
        return self.path_shp_input
    
    def handle_radios(self):
        """
            Controlar exibição de caixas de entrada através de radio buttons
        """
        if self.rdbtn_pdf.isChecked():
            self.btn_input.setVisible(True)
            self.lbl_input.setVisible(True)
            self.txt_input.setVisible(True)

            self.txt_copy.setVisible(False)
            self.lbl_copy.setVisible(False)
        else:
            self.btn_input.setVisible(False)
            self.lbl_input.setVisible(False)
            self.txt_input.setVisible(False)

            self.txt_copy.setVisible(True)
            self.lbl_copy.setVisible(True)

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
        self.txt_copied = self.txt_copy.toPlainText()
        # Testa se o diretório do pdf de entrada foi inserido
        if (self.path_input != "") or (self.txt_copied != ""):
            
            lista_coords = self.extrai_coords()
            lyr_pdf = self.gerar_layer(lista_coords)

            self.hide()

        else:
            if self.rdbtn_pdf.isChecked():
                self.iface.messageBar().pushMessage("Error", "Selecione um pdf de entrada.", level=1)
            else:
                self.iface.messageBar().pushMessage("Error", "Cole o conteudo copiado na caixa de texto.", level=1)

    def extrai_coords(self):
        """
            Função que extrai coordenadas de pdf's usando REGEX
        """
        if self.ex_coords == "":
            self.iface.messageBar().pushMessage("Error", "Insira um exemplo de par de coordenadas do texto pdf ou copiado.", level=1)
        else:
            regex_str = self.get_regex_from_str(self.ex_coords)

            if self.rdbtn_pdf.isChecked():
                pdfFileObj = open(self.path_input, 'rb')

                pdf_reader = PyPDF2.PdfReader(pdfFileObj)
                totalPages = len(pdf_reader.pages)
                text_out = ""
                

                for i in range(0, totalPages):
                    pages = pdf_reader.pages[i]
                    text = pages.extract_text()
                    text_out += text.replace("\n", "").replace(" ", "")

                lista_coords = re.findall(regex_str, text_out)
            else:
                lista_coords = re.findall(regex_str, self.txt_copied.replace("\n", "").replace(" ", ""))

            return lista_coords
    
    def gerar_layer(self, lista):
        """
            Função para geração de layer de geometria extraida, a partir de coordenadas
        """
        if len(lista) > 1:
            mem_layer = QgsVectorLayer(f"Polygon?crs={self.select_crs.crs().authid().lower()}", "Memorial Descritivo - PDF", "Memory")
            QgsProject.instance().addMapLayer(mem_layer)
            poly_coords = []
            # split_by = self.combo_seperador.currentText()
            split_by = self.combo_seperador.currentText()
            first_lat = True if self.combo_lat_long.currentText() == "Latitude" else False

            split_by = fr"(?<=\d){split_by}(?=[A-Za-z])|(?<=[A-Za-z]){split_by}(?=\d)"
            
            for idx, coords in enumerate(lista):
                latitude = ""
                longitude = ""
                coords = coords.replace("m", "")
                vertice = re.split(split_by, coords)[1 if first_lat else 0]
                for i, char in enumerate(vertice):
                    if char.isdigit():
                        latitude = str(latitude) + char

                    elif char == ",":
                        if i > 0 and i < len(vertice):
                            if vertice[i - 1].isdigit() and vertice[i + 1].isdigit():
                                latitude = str(latitude) + "."
                vertice = re.split(split_by, coords)[0 if first_lat else 1]
                for i, char in enumerate(vertice):
                    if char.isdigit():
                        longitude = str(longitude) + char

                    elif char == ",":
                        if i > 0 and i < len(vertice) - 1:
                            if vertice[i - 1].isdigit() and vertice[i + 1].isdigit():
                                longitude = str(longitude) + "."

                poly_coords.append((float(longitude), float(latitude)))

            polygon = QgsGeometry.fromPolygonXY( [[ QgsPointXY( pair[0], pair[1] ) for pair in poly_coords ]])
            feature = QgsFeature()
            feature.setGeometry(polygon)
            mem_layer.dataProvider().addFeatures([feature])

            return mem_layer
        else:
            self.iface.messageBar().pushMessage("Error", "Não foi possível gerar a geometria. Verifique o texto inserido e o par de coordenadas de exemplo.", level=1)

    def get_regex_from_str(self, string):
        """
            Função que extrai padrão REGEX a partir de par de coordenada passado como exemplo
        """
        
        str_return = ""
        for character in string:
            if character.isdigit():
                str_return += '\d'
            elif character.isspace():
                pass
            else:
                str_return += character
        return str_return

            