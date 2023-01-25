import sys, json, os
sys.path.append(r"C:\Users\Marco Reliquias\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\prisma\settings")

from qgis.core import *

# ### Inicializando  ####
qgs = QgsApplication([], True)
qgs.initQgis()
QgsApplication.setPrefixPath(r"C:\OSGeo4W\apps\qgis", True)
sys.path.append(r"C:\OSGeo4W\apps\qgis\python\plugins")
QgsApplication.initQgis()


def get_config_shapefile(json_path):

    """
    Retorna uma lista com as configurações de bases em ShapeFile.
    @return: Lista com as configurações.
    """
    shp_list = []

    if os.stat(json_path).st_size != 0:
        with open(json_path, 'r', encoding='utf8') as f:
            json_config = json.load(f)
            f.close()

        for base, data in json_config.items():
            if 'tipo' in data and data['tipo'] == 'shp':
                shp_list.append(data)

    return shp_list

db_json = r"D:\Zago\bkp dbtabases\dbtabases.json"
project = r'C:\Users\Marco Reliquias\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\prisma\qgis\layouts\SPU-PRISMA_2.0_atlas.qgz'
qgs_instance = QgsProject.instance()
qgs_instance.read(project)
my_layout = qgs_instance.layoutManager().layoutByName('Exemplo_tabela')

tabla = my_layout.itemById('tabela1')
tabla_item = tabla.multiFrame()
source_shp = get_config_shapefile(db_json)

for idx, shp in enumerate(source_shp):
    nome = shp['nomeFantasiaCamada']
    caminho = shp['diretorioLocal']
    selectedFields = shp['selectedFields']
    if selectedFields[0] != "" and selectedFields[1] != "" and selectedFields[2] != "":
        layer = QgsVectorLayer(caminho, f"{nome}",  "ogr")
        tabla_item.setVectorLayer(layer)
        tabla_item.setDisplayedFields(selectedFields)
        
        exporter = QgsLayoutExporter(my_layout)

        result= exporter.exportToPdf(fr"C:\Users\Marco Reliquias\Desktop\Teste\{idx}.pdf", QgsLayoutExporter.PdfExportSettings())
        if not result == exporter.Success:
            print(result)
