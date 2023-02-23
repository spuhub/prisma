import os
from qgis import processing
from qgis.core import QgsVectorLayer

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


def lyr_input_process(layer_in:QgsVectorLayer, crs_out:int=4326) -> QgsVectorLayer:
    lyr_reproj = layer_reproject(layer_in, crs_out)

    lyr_fixed = layer_fix_geometries(lyr_reproj)

    lyr_return = layer_get_sirgas_epsg(lyr_fixed)
    lyr_return.setName(layer_in.name())

    return lyr_return