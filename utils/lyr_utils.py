import os

from qgis import processing
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsWkbTypes
    )

from ..environment import (
    NOME_CAMADA_ENTRADA,
    NOME_CAMADA_ENTRADA_BUFFER,
    NOME_CAMADA_INTERSECAO_PONTO,
    NOME_CAMADA_INTERSECAO_LINHA,
    NOME_CAMADA_INTERSECAO_POLIGONO,
    CAMADA_DE_PONTO,
    CAMADA_DE_LINHA,
    CAMADA_DE_POLIGONO,
    NOME_CAMADA_VERTICES,
    NOME_CAMADA_QUOTAS,
    CRS_PADRAO
)

from .default_styles import default_styles

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
    lyr_return = add_style(lyr_return, operation_config)

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
    if layer.name() == NOME_CAMADA_ENTRADA:
        layer = layer.clone()
        
    buffered_layer = QgsVectorLayer(f'MultiPolygon?crs=epsg:{CRS_PADRAO}', NOME_CAMADA_ENTRADA_BUFFER, 'memory')

    # Copia os campos da camada de entrada para a camade de buffer
    fields = layer.fields()
    buffered_layer.dataProvider().addAttributes(fields)
    buffered_layer.updateFields()

    # Habilita a edição da camada    
    buffered_layer.startEditing()

    # Itera sobre as features da camada, aplica o buffer e atualiza a geometria
    for feature in layer.getFeatures():
        # Adicionar na camada de buffer as feições com os mesmos valores presentes na camada de entrada
        new_feature = QgsFeature(buffered_layer.fields())
        new_feature.setAttributes(feature.attributes())

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
        #buffered_layer.changeGeometry(feature.id(), buffered_geometry)
        new_feature.setGeometry(buffered_geometry)
        buffered_layer.addFeature(new_feature)

    # Salva as mudanças na nova camada
    buffered_layer.commitChanges()

    return buffered_layer

def add_style(layer: QgsVectorLayer, operation_config: dict):
    """
    Aplica um estilo SLD a uma camada QgsVectorLayer.

    Parameters:
        layer (QgsVectorLayer): camada QgsVectorLayer a ser estilizada
        operation_config (dict): dicionário com as configurações da operação, incluindo o caminho para os arquivos SLD

    Returns:
        QgsVectorLayer: camada estilizada com o SLD
    """
    if layer.name() == NOME_CAMADA_VERTICES:
        layer.loadNamedStyle(default_styles.VERTICES_LAYER.get_path())
        layer.triggerRepaint()

        return layer
    
    if layer.name() == NOME_CAMADA_QUOTAS:
        layer.loadNamedStyle(default_styles.QUOTAS_LAYER.get_path())
        layer.triggerRepaint()

        return layer

    sld_path: str = ''
    if layer.name() == NOME_CAMADA_ENTRADA:
        # Identifica o tipo de geometria da camada
        geometry_type = get_general_geom_type_name(layer)

        # Seleciona o caminho para o arquivo SLD apropriado
        if geometry_type in CAMADA_DE_PONTO:  # Ponto
            sld_path = operation_config['sld_default_layers']['default_input_point']
        elif geometry_type in CAMADA_DE_LINHA:  # Linha
            sld_path = operation_config['sld_default_layers']['default_input_line']
        elif geometry_type in CAMADA_DE_POLIGONO:  # Polígono
            sld_path = operation_config['sld_default_layers']['default_input_polygon']
        else:
            raise ValueError(f"Tipo de geometria inválido: {geometry_type}")
        
    elif layer.name() == NOME_CAMADA_ENTRADA_BUFFER:
        sld_path = operation_config['sld_default_layers']['buffer']
    
    elif layer.name() in [NOME_CAMADA_INTERSECAO_PONTO, NOME_CAMADA_INTERSECAO_LINHA, NOME_CAMADA_INTERSECAO_POLIGONO]:
        # Identifica o tipo de geometria da camada
        geometry_type = get_general_geom_type_name(layer)
        # Seleciona o caminho para o arquivo SLD apropriado
        if geometry_type in CAMADA_DE_PONTO:  # Ponto
            sld_path = operation_config['sld_default_layers']['overlay_input_point']
        elif geometry_type in CAMADA_DE_LINHA:  # Linha
            sld_path = operation_config['sld_default_layers']['overlay_input_line']
        elif geometry_type in CAMADA_DE_POLIGONO:  # Polígono
            sld_path = operation_config['sld_default_layers']['overlay_input_polygon']
        else:
            raise ValueError(f"Tipo de geometria inválido: {geometry_type}")

    else:
        for layer_shp in operation_config['shp']:
            if layer.name() == layer_shp['nomeFantasiaCamada']:
                sld_path = layer_shp['estiloCamadas']
        
        for layer_db in operation_config['pg']:
            if layer.name() == layer_db['nomeFantasiaCamada']:
                sld_path = layer_db['estiloCamadas']

        for layer_wfs in operation_config['wfs']:
            if layer.name() == layer_wfs['nomeFantasiaCamada']:
                sld_path = layer_wfs['estiloCamadas']

        for layer_required in operation_config['obrigatorio']:
            if layer.name() == layer_required['nomeFantasiaCamada']:
                sld_path = layer_required['estiloCamadas']

    # Identifica o tipo de estilo para a camada e o aplica
    print(sld_path)
    if sld_path.endswith('.qml'):
        layer.loadNamedStyle(os.path.normpath(sld_path))
    elif sld_path.endswith('.sld'):
        layer.loadSldStyle(os.path.normpath(sld_path))

    layer.triggerRepaint()

    # TODO: Atualiza o estilo da camada no projeto
    # QgsProject.instance().write()

    return layer

def export_atlas_single_page(layer: QgsVectorLayer, feature: QgsFeature, layout_name: str, pdf_name: str, path_output: str, suffix: str) -> None:
    logradouro = feature['logradouro']

    parameters = {
        "COVERAGE_LAYER" : layer,
        "DPI" : 200,
        "FILTER_EXPRESSION" : f"logradouro='{logradouro}'",
        "FORCE_VECTOR" : False,
        "GEOREFERENCE" : True,
        "INCLUDE_METADATA" : True,
        "LAYERS" : None,
        "LAYOUT" : layout_name,
        "OUTPUT" : f"{path_output}/{pdf_name}_{suffix}.pdf",
        "SIMPLIFY" : True,
        "SORTBY_EXPRESSION" : "$id",
        "SORTBY_REVERSE" : False,
        "TEXT_FORMAT" : 0
        }
    processing.run("native:atlaslayouttopdf", parameters)

def get_general_geom_type_name(geom):
        geom_type = geom.geometryType()
        if geom_type == QgsWkbTypes.PointGeometry:
            return 'Point'
        elif geom_type == QgsWkbTypes.LineGeometry:
            return 'LineString'
        elif geom_type == QgsWkbTypes.PolygonGeometry:
            return 'Polygon'
