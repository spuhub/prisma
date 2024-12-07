# -*- coding: utf-8 -*-
from qgis.PyQt.QtWidgets import QApplication
from qgis.core import QgsProject, QgsRasterLayer, QgsCoordinateReferenceSystem
from qgis.utils import iface

from ..utils.utils import Utils

class MapCanvas():
    """
    Classe responsável por gerenciar o canvas de mapas no QGIS.

    Fornece funcionalidade para exibir todas as camadas utilizadas na comparação
    ou apenas as camadas que possuem sobreposições.
    """
    def __init__(self):
        """Método construtor da classe."""
        self.data = None
        self.utils = Utils()
        self.basemap_name, self.basemap_link = self.utils.get_active_basemap()


    def print_all_layers_qgis(self, data):
        """
        Exibe no canvas do QGIS todas as camadas que estão sendo comparadas.

        Args:
            data (dict): Dicionário com configurações da operação, contendo:
                - `input`: camada de entrada.
                - `input_buffer`: buffer da camada de entrada (se existir).
                - `lyr_overlap_*`: camadas de sobreposição (se existirem).
                - `shp`, `wfs`, `db`: camadas selecionadas para comparação.
                - `required`: camadas obrigatórias.
                - `operation_config`: configuração da operação.
        """
        self.data = data
        input = data['layers']['input']
        input_buffer = data['layers']['input_buffer'] if 'input_buffer' in data['layers'] else None
        lyr_overlap_point = data['layers']['lyr_overlap_point'] if 'lyr_overlap_point' in data['layers'] else None
        lyr_overlap_line = data['layers']['lyr_overlap_line'] if 'lyr_overlap_line' in data['layers'] else None
        lyr_overlap_polygon = data['layers']['lyr_overlap_polygon'] if 'lyr_overlap_polygon' in data['layers'] else None
        lyr_vertices = data['layers']['lyr_vertices'] if 'lyr_vertices' in data['layers'] else None

        list_selected_shp = data['layers']['shp']
        list_selected_wfs = data['layers']['wfs']
        list_selected_db = data['layers']['db']
        list_selected_required = data['layers']['required']

        lista_layers = []
        if input_buffer:
            lista_layers = [input_buffer]
            lista_layers += [input]
        else:
            lista_layers = [input]
        lista_layers += list_selected_required + list_selected_db + list_selected_shp + list_selected_wfs

        if lyr_overlap_point:
            lista_layers += [lyr_overlap_point]
        if lyr_overlap_line:
            lista_layers += [lyr_overlap_line]
        if lyr_overlap_polygon:
            lista_layers += [lyr_overlap_polygon]
        if lyr_vertices:
            lista_layers += [lyr_vertices]

        if 'basemap' in data['operation_config']:
            layer = QgsRasterLayer(self.basemap_link, self.basemap_name, 'wms')
        else:
            # Carrega camada mundial do OpenStreetMap
            tms = 'type=xyz&url=http://a.tile.openstreetmap.org/{z}/{x}/{y}.png'
            layer = QgsRasterLayer(tms, 'OpenStreetMap', 'wms')

        QgsProject.instance().addMapLayer(layer)
        QgsProject.instance().setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
        QApplication.instance().processEvents()

        for layer in lista_layers:
            QgsProject.instance().addMapLayer(layer.clone())
        
        # Repaint the canvas map
        iface.mapCanvas().refresh()
        # Da zoom na camada de input
        iface.zoomToActiveLayer()

    def print_overlay_qgis(self, data):
        """
        Exibe no canvas do QGIS apenas as camadas que apresentaram sobreposição.

        Args:
            data (dict): Dicionário com configurações da operação, contendo:
                - `input`: camada de entrada.
                - `input_buffer`: buffer da camada de entrada (se existir).
                - `lyr_overlap_*`: camadas de sobreposição (se existirem).
                - `overlaps`: dicionário com camadas sobrepostas.
                - `operation_config`: configuração da operação.
        """
        self.data = data
        input = data['layers']['input']
        input_buffer = data['layers']['input_buffer'] if 'input_buffer' in data['layers'] else None
        lyr_overlap_point = data['layers']['lyr_overlap_point'] if 'lyr_overlap_point' in data['layers'] else None
        lyr_overlap_line = data['layers']['lyr_overlap_line'] if 'lyr_overlap_line' in data['layers'] else None
        lyr_overlap_polygon = data['layers']['lyr_overlap_polygon'] if 'lyr_overlap_polygon' in data['layers'] else None
        lyr_vertices = data['layers']['lyr_vertices'] if 'lyr_vertices' in data['layers'] else None
        list_overlaps = data['overlaps']
        list_overlaps = [list_overlaps[item][0] for item in list_overlaps]

        if input_buffer:
            lista_layers = [input_buffer]
            lista_layers += [input]
        else:
            lista_layers = [input]
        if lyr_overlap_point:
            lista_layers += [lyr_overlap_point]
        if lyr_overlap_line:
            lista_layers += [lyr_overlap_line]
        if lyr_overlap_polygon:
            lista_layers += [lyr_overlap_polygon]
        if lyr_vertices:
            lista_layers += [lyr_vertices]
        lista_layers += list_overlaps

        if 'basemap' in data['operation_config']:
            layer = QgsRasterLayer(self.basemap_link, self.basemap_name, 'wms')
        else:
            # Carrega camada mundial do OpenStreetMap
            tms = 'type=xyz&url=http://a.tile.openstreetmap.org/{z}/{x}/{y}.png'
            layer = QgsRasterLayer(tms, 'OpenStreetMap', 'wms')

        QgsProject.instance().addMapLayer(layer)
        QgsProject.instance().setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
        QApplication.instance().processEvents()

        for layer in lista_layers:
            QgsProject.instance().addMapLayer(layer.clone())

            # Repaint the canvas map
            iface.mapCanvas().refresh()
            # Da zoom na camada de input
            iface.zoomToActiveLayer()
