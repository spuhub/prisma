from qgis.PyQt import QtGui

from qgis.core import QgsVectorLayer, QgsField, QgsApplication
from qgis.core import QgsProject, QgsLayoutExporter, Qgis

class LayoutManager():
    def __init__(self) -> None:
        super().__init__()
        self.export_pdf()

    def export_pdf(self):
        layers = QgsProject.instance().mapLayersByName('input')
        layer = layers[0]

        project = QgsProject.instance()
        manager = project.layoutManager()
        
        layout = self.open_layout('FolhaA3_Planta_Paisagem')

        atlas = layout.atlas()
        map_atlas = atlas.layout()

        pdf_settings = QgsLayoutExporter(map_atlas).PdfExportSettings()
        pdf_settings.dpi = 150

        ms = QgsMapSettings()
        ms.setLayers([layer]) # set layers to be mapped

        rect = QgsRectangle(ms.fullExtent())
        rect.scale(1.0)
        ms.setExtent(rect)

        map = layout.itemById('Planta_Principal')
        map.setRect(20, 20, 20, 20)
        map.setExtent(rect)

        # map.attemptMove(QgisLayoutPoint(5, 20))



    def open_layout(self, layout_name):
        atlas_project_path = QgsApplication.qgisSettingsDirPath() + r'\python\plugins\prisma\layout\Projeto_com_Layout_A3.qgz'
        
        QgsProject.instance().read(atlas_project_path)
        layout = QgsProject.instance().layoutManager().layoutByName('FolhaA3_Planta_Paisagem')

        return layout