import os

from qgis.core import *
from qgis.PyQt.QtXml import QDomDocument
from qgis.utils import iface

class LayoutManager():
    def __init__(self, result):
        super().__init__()
        self.result = result
        # Adiciona o layout ao projeto atual
        template_dir = os.path.join(os.path.dirname(__file__), 'layouts\Modelo_Layout_A3.qpt')
        self.add_template_to_project(template_dir)

        # Armazena na variável o layout que acabou de ser adicionado
        # ao projeto, permitindo a manipulação do mesmo
        self.layout = QgsProject.instance().layoutManager().layoutByName("FolhaA3_Planta_Retrato")
        self.layers = []

    def export_pdf(self):
        # Armazena as camadas em self.layers e adiciona as camadas no QGis
        self.load_layers()
        # Manipulação dos textos do layout
        self.handle_text()

        pdf_path = os.path.join(r'C:\Users\vinir\Documents\saida', "output.pdf")
        exporter = QgsLayoutExporter(self.layout)
        exporter.exportToPdf(pdf_path, QgsLayoutExporter.PdfExportSettings())

    def handle_text(self):
        title = self.layout.itemById('CD_Titulo')
        title.setText('Teste 123')

        scale = self.layout.itemById('CD_Escala')
        scale.setText('1:' + str(round(iface.mapCanvas().scale())))

    def load_layers(self):
        self.layers.append(QgsProject.instance().mapLayersByName('input')[0])

        # Pega camadas através dos nomes
        if len(self.result['operation_config']['shp']) != 0:
            print(len(self.result['operation_config']['shp']))
            for i in range(len(self.result['operation_config']['shp'])):
                vlayer = QgsProject.instance().mapLayersByName(self.result['operation_config']['shp'][i]['nomeFantasiaCamada'])
                if len(vlayer) > 0:
                    self.layers.append(vlayer[0])

        if len(self.result['operation_config']['pg']) != 0:
            print(len(self.result['operation_config']['pg']))
            for i in range(len(self.result['operation_config']['pg'])):
                for j in range(len(self.result['operation_config']['pg'][i]['nomeFantasiaTabelasCamadas'])):
                    vlayer = QgsProject.instance().mapLayersByName(self.result['operation_config']['pg'][i]['nomeFantasiaTabelasCamadas'][j])
                    if len(vlayer) > 0:
                        self.layers.append(vlayer[0])

        ms = QgsMapSettings()
        ms.setLayers(self.layers)
        rect = QgsRectangle(ms.fullExtent())
        rect.scale(1.0)

        map = self.layout.itemById('Planta_Principal')

        ms.setExtent(rect)
        map.setExtent(rect)

        # Tamanho do mapa no layout
        map.attemptResize(QgsLayoutSize(390, 277, QgsUnitTypes.LayoutMillimeters))

    def add_template_to_project(self, template_dir):
        project = QgsProject.instance()
        layout = QgsPrintLayout(project)
        document = QDomDocument()

        # Leitura do template
        template_file = open(template_dir)
        template_content = template_file.read()
        template_file.close()
        document.setContent(template_content)

        # Adição do template no projeto
        layout.loadFromTemplate(document, QgsReadWriteContext())
        project.layoutManager().addLayout(layout)
