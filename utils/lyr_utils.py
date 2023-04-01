import os

from qgis import processing
from qgis.core import (QgsProject,QgsVectorLayer, QgsCoordinateTransform, QgsCoordinateReferenceSystem)

from ..environment import CAMADA_ENTRADA, CRS_PADRAO

def layer_reproject(layer_in:QgsVectorLayer, crs_out:int=4326) -> QgsVectorLayer:
    '''
        Função de apoio para execução de ferramenta de reprojeção do QGIS.
            Parameters:
                layer_in (QgsVectorLayer): Objeto QgsVectorLayer a ser reprojetado
                crs_out (int): Código EPSG do Sistema de referencia de saída

            Returns:
                Memory_out (QgsVectorLayer): Objeto QgsVectorLayer em memória do objeto reprojetado
    '''
    parameter = {'INPUT': layer_in,
                 'TARGET_CRS': f'EPSG:{crs_out}',
                 'OUTPUT': 'memory:'
                }
    lyr_return = processing.run('native:reprojectlayer', parameter)['OUTPUT']

    return lyr_return
    
def layer_fix_geometries(layer_in:QgsVectorLayer) -> QgsVectorLayer:
    '''
        Função de apoio para execução de ferramenta de correção de geometrias do QGIS.
            Parameters:
                layer_in (QgsVectorLayer): Objeto QgsVectorLayer a ser corrigido
                
            Returns:
                Memory_out (QgsVectorLayer): Objeto QgsVectorLayer em memória do objeto corrigido
    '''
    parameter = {'INPUT': layer_in,
                 'OUTPUT': 'memory:'
                }
    lyr_return = processing.run('native:fixgeometries', parameter)['OUTPUT']

    return lyr_return

def layer_get_sirgas_epsg(layer_in:QgsVectorLayer) -> QgsVectorLayer:
    '''
        Função de apoio para identificação de Zona Sirgas 2000.
            Parameters:
                layer_in (QgsVectorLayer): Objeto QgsVectorLayer de entrada
                
            Returns:
                Memory_out (QgsVectorLayer): Objeto QgsVectorLayer em memória do objeto com as zonas
    '''
    shp_zonas_sirgas = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                    'shapefiles', 
                                    'Zonas_UTM_BR-EPSG4326.shp')
    lyr_zonas_sirgas = QgsVectorLayer(shp_zonas_sirgas, 'Zonas_Sirgas', 'ogr')
    parameter = {'INPUT': layer_in,
                 'JOIN': lyr_zonas_sirgas,
                 'PREDICATE':[0],
                 'JOIN_FIELDS':['EPSG_S2000'],
                 'METHOD':2,
                 'DISCARD_NONMATCHING':False,
                 'PREFIX':'',
                 'OUTPUT':'memory:'}
    lyr_return = processing.run("native:joinattributesbylocation", parameter)['OUTPUT']

    return lyr_return

def lyr_process(layer_in:QgsVectorLayer, operation_config: dict, crs_out:int=4326) -> QgsVectorLayer:
    '''
        Função de chamada para processar todas as ferramentas no layer de entrada.
            Parameters:
                layer_in (QgsVectorLayer): Objeto QgsVectorLayer a ser reprojetado
                operation_config (dict): Dicionário contendo configurações das camadas utilizadas
                crs_out (int): Código EPSG do Sistema de referencia de saída

            Returns:
                Memory_out (QgsVectorLayer): Objeto QgsVectorLayer em memória do layer de 
                                             entrada com processamentos realizados
    '''
    lyr_reproj = layer_reproject(layer_in, crs_out)
    lyr_fixed = layer_fix_geometries(lyr_reproj)
    lyr_return = layer_get_sirgas_epsg(lyr_fixed)

    lyr_return.setName(layer_in.name())

    return lyr_return

def insert_buffer(layer: QgsVectorLayer, buffer_size: int) -> QgsVectorLayer:
    """
    Insere um buffer de tamanho especificado em todas as geometrias de uma camada do tipo QgsVectorLayer.

    Parameters:
        layer (QgsVectorLayer): Camada a ser bufferizada.
        buffer_size (int): Tamanho do buffer em unidades do sistema de coordenadas da camada.

    Returns:
        QgsVectorLayer: A camada com as geometrias bufferizadas.
    """
    if layer.name() == CAMADA_ENTRADA:
        layer = layer.clone()
        
    # Habilita a edição da camada    
    layer.startEditing()

    # Itera sobre as features da camada, aplica o buffer e atualiza a geometria
    for feature in layer.getFeatures():
        geometry = feature.geometry()

        # Obtém o EPSG do atributo "ESPG_S2000" e cria o objeto CRS correspondente
        epsg = feature.attribute('EPSG_S2000')
        layer_crs = QgsCoordinateReferenceSystem(f'EPSG:{epsg}')
        default_crs = QgsCoordinateReferenceSystem(f'EPSG:{CRS_PADRAO}')

        # Cria as instâncias dos objetos de transformação de coordenadas
        coord_transform_in = QgsCoordinateTransform(default_crs, layer_crs, QgsProject.instance())
        coord_transform_out = QgsCoordinateTransform(layer_crs, default_crs, QgsProject.instance())

        # Converte a geometria para o CRS de destino
        geometry.transform(coord_transform_in)

        # Insere o buffer na geometria
        buffered_geometry = geometry.buffer(buffer_size, 5)

        # Converte a geometria de volta para o CRS original
        buffered_geometry.transform(coord_transform_out)

        # Atualiza a geometria da feature
        layer.changeGeometry(feature.id(), buffered_geometry)

    # Salva as mudanças e finaliza a edição da camada
    layer.commitChanges()

    return layer

def add_style(layer: QgsVectorLayer, sld_dir: str):
    """
    Aplica um estilo SLD a uma camada QgsVectorLayer.

    Parameters:
        layer (QgsVectorLayer): camada QgsVectorLayer a ser estilizada
        sld_dir (str): caminho para o arquivo SLD a ser aplicado

    """
    # Abre o arquivo SLD e carrega seu conteúdo em um objeto QDomDocument
    layer.loadSldStyle(sld_dir)
    layer.triggerRepaint()

    # Update the layer's style in the project
    # QgsProject.instance().write()

    return layer

def export_atlas_single_page(layer: QgsVectorLayer, layout_name: str, path_output: str) -> None:
    for feature in layer.getFeatures():
        logradouro = feature['logradouro']
        logradouro = logradouro.replace(".", ' ').replace("/", "_").replace("'", "")
        parameters = {
            "COVERAGE_LAYER" : layer,
            "DPI" : 60,
            "FILTER_EXPRESSION" : f"logradouro='{logradouro}'",
            "FORCE_VECTOR" : False,
            "GEOREFERENCE" : True,
            "INCLUDE_METADATA" : True,
            "LAYERS" : None,
            "LAYOUT" : layout_name,
            "OUTPUT" : f"{path_output}/{logradouro}.pdf",
            "SIMPLIFY" : True,
            "SORTBY_EXPRESSION" : "$id",
            "SORTBY_REVERSE" : False,
            "TEXT_FORMAT" : 0
            }
        processing.run("native:atlaslayouttopdf", parameters)
    