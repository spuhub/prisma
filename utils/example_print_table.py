

project = r'C:\Users\Marco Reliquias\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\prisma\qgis\layouts\SPU-PRISMA_2.0_atlas.qgz'
QgsProject.instance().read(my_project)
my_layout = QgsProject.instance().layoutManager().layoutByName(layout_name)