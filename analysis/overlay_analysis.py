# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Prisma
                                 A QGIS plugin
 Plugin para fazer caracterização de imóveis
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-09-29
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Zago
        email                : guilherme.nascimento@economia.gov.br; vinirafaelsch@gmail.com; vinirafaelsch@gmail.com; marcoaurelio.reliquias@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from ..utils.utils import Utils
from qgis.core import QgsFeature, QgsVectorLayer, QgsWkbTypes, QgsGeometry, QgsField, QgsFields, QgsPointXY, QgsCoordinateReferenceSystem, QgsProject, QgsCoordinateTransform
from ..utils.lyr_utils import lyr_process
from qgis.PyQt.QtCore import QVariant

from ..environment import (
    CRS_PADRAO,
    NOME_CAMADA_INTERSECAO_PONTO,
    NOME_CAMADA_INTERSECAO_LINHA,
    NOME_CAMADA_INTERSECAO_POLIGONO,
    NOME_CAMADA_VERTICES
)

class OverlayAnalisys():
    """
    Classe utilizada para verificar quais áreas possuem sobreposição entre input de entrada e camadas de comparação.

    @ivar operation_config: Dicionário que armazena configurações de operação, como por exemplo: dado de input, bases de dados selecionadas para comparação, busca por ponto, shapefile, etc...
    @ivar shp_handle: Armazena classe para leitura de arquivos shapefile.
    @ivar utils: Armazena classe contendo algumas funções úteis para o código.
    """
    def __init__(self):
        """Método construtor da classe."""
        self.provider_point = None
        self.provider_line = None
        self.provider_polygon = None
        self.utils = Utils()

    def overlay_analysis(self, dic_layers, operation_config):
        """
        Função que conta quantas sobreposições aconteceram entre a camada de input e as todas as camadas de comparação selecionadas.
        Esta função é feita através da projeção geográfica.

        @keyword operation_config: Dicionário que armazena configurações de operação, como por exemplo: dado de input, bases de dados selecionadas para comparação, busca por ponto, shapefile, etc...
        @return result: Dicionário que retorna, no formato de geodataframe, todas camadas passadas para comparação e também as camadas que tiveram sobreposição.
        """
        self.operation_config = operation_config

        lyr_input = None
        if 'input_buffer' in dic_layers:
            lyr_input = dic_layers['input_buffer']
        else:
            lyr_input = dic_layers['input']
            
        list_required = dic_layers['required']
        list_selected_shp = dic_layers['shp']
        list_selected_wfs = dic_layers['wfs']
        list_selected_db = dic_layers['db']

        feats_input = lyr_input.getFeatures()
        lyr_input.selectAll()
        bbox_lyr_input = lyr_input.boundingBoxOfSelected()

        # Cria em memória a camada de interseção
        self.lyr_overlap_point = QgsVectorLayer(f'MultiPoint?crs=epsg:{CRS_PADRAO}', NOME_CAMADA_INTERSECAO_PONTO, 'memory')
        self.lyr_overlap_line = QgsVectorLayer(f'MultiLineString?crs=epsg:{CRS_PADRAO}', NOME_CAMADA_INTERSECAO_LINHA, 'memory')
        self.lyr_overlap_polygon = QgsVectorLayer(f'MultiPolygon?crs=epsg:{CRS_PADRAO}', NOME_CAMADA_INTERSECAO_POLIGONO, 'memory')
        lyr_vertices = QgsVectorLayer(f'Point?crs=epsg:{CRS_PADRAO}', NOME_CAMADA_VERTICES, 'memory')

        # Extrai vértices da camada de entrada
        if lyr_input.wkbType() == QgsWkbTypes.Polygon or lyr_input.wkbType() == QgsWkbTypes.MultiPolygon:
            lyr_vertices = self._extract_polygon_vertices(lyr_input)
            lyr_vertices = lyr_process(lyr_vertices, operation_config)
        
        fields = lyr_input.fields()
        novo_campo = QgsField('Camada_sobreposicao', QVariant.String)
        fields.append(novo_campo)

        self.provider_point = self.lyr_overlap_point.dataProvider()
        self.provider_point.addAttributes(fields)

        self.provider_line = self.lyr_overlap_line.dataProvider()
        self.provider_line.addAttributes(fields)

        self.provider_polygon = self.lyr_overlap_polygon.dataProvider()
        self.provider_polygon.addAttributes(fields)

        self.lyr_overlap_point.updateFields()
        self.lyr_overlap_line.updateFields()
        self.lyr_overlap_polygon.updateFields()
                
        dic_overlaps = {}
        lyr_input.startEditing()
        self.lyr_overlap_point.startEditing()
        self.lyr_overlap_line.startEditing()
        self.lyr_overlap_polygon.startEditing()
        
        for feat in feats_input:
            feat_geom = feat.geometry()

            for lyr_shp in list_selected_shp:
                index = lyr_input.fields().indexFromName(lyr_shp.name())
                # Início dos processos para comparação
                feats_shp = lyr_shp.getFeatures(bbox_lyr_input)

                for feat_shp in feats_shp:
                    feat_shp_geom = feat_shp.geometry()

                    if feat_geom.intersects(feat_shp_geom):
                        if lyr_shp.name() not in dic_overlaps:
                            dic_overlaps[lyr_shp.name()] = [lyr_shp, 1]
                        else:
                            dic_overlaps[lyr_shp.name()][1] += 1

                        lyr_input.changeAttributeValue(feat.id(), index, True)
                        self._create_overlap_feature(feat_geom, feat_shp_geom, feat, lyr_shp.name())
            
            for lyr_db in list_selected_db:
                index = lyr_input.fields().indexFromName(lyr_db.name())
                feats_db = lyr_db.getFeatures(bbox_lyr_input)

                for feat_db in feats_db:
                    feat_db_geom = feat_db.geometry()

                    if feat_geom.intersects(feat_db_geom):
                        if lyr_db.name() not in dic_overlaps:
                            dic_overlaps[lyr_db.name()] = [lyr_db, 1]
                        else:
                            dic_overlaps[lyr_db.name()][1] += 1

                        lyr_input.changeAttributeValue(feat.id(), index, True)
                        self._create_overlap_feature(feat_geom, feat_db_geom, feat, lyr_db.name())
            
            for lyr_wfs in list_selected_wfs:
                index = lyr_input.fields().indexFromName(lyr_wfs.name())
                feats_wfs = lyr_wfs.getFeatures(bbox_lyr_input)

                for feat_wfs in feats_wfs:
                    feat_wfs_geom = feat_wfs.geometry()

                    if feat_geom.intersects(feat_wfs_geom):
                        if lyr_wfs.name() not in dic_overlaps:
                            dic_overlaps[lyr_wfs.name()] = [lyr_wfs, 1]
                        else:
                            dic_overlaps[lyr_wfs.name()][1] += 1
                        
                        lyr_input.changeAttributeValue(feat.id(), index, True)
                        self._create_overlap_feature(feat_geom, feat_wfs_geom, feat, lyr_wfs.name())

            for lyr_req in list_required:
                index = lyr_input.fields().indexFromName(lyr_req.name())
                feats_req = lyr_req.getFeatures(bbox_lyr_input)

                for feat_req in feats_req:
                    feat_req_geom = feat_req.geometry()

                    if feat_geom.intersects(feat_req_geom):
                        if lyr_req.name() not in dic_overlaps:
                            dic_overlaps[lyr_req.name()] = [lyr_req, 1]
                        else:
                            dic_overlaps[lyr_req.name()][1] += 1

                        lyr_input.changeAttributeValue(feat.id(), index, True)
                        self._create_overlap_feature(feat_geom, feat_req_geom, feat, lyr_req.name())

        # Atualiza camada de entrada
        lyr_input.commitChanges()

        # Adiciona os estilos às camadas de sobreposição
        self.lyr_overlap_point = lyr_process(self.lyr_overlap_point, operation_config)
        self.lyr_overlap_line = lyr_process(self.lyr_overlap_line, operation_config)
        self.lyr_overlap_polygon = lyr_process(self.lyr_overlap_polygon, operation_config)

        # Seta como None a variável caso não tenha nenhuma sobreposição
        if self.lyr_overlap_point.featureCount() == 0:
            self.lyr_overlap_point = None
        if self.lyr_overlap_line.featureCount() == 0:
            self.lyr_overlap_line = None
        if self.lyr_overlap_polygon.featureCount() == 0:
            self.lyr_overlap_polygon = None
        if lyr_vertices.featureCount() == 0:
            lyr_vertices = None
        
        return dic_overlaps, self.lyr_overlap_point, self.lyr_overlap_line, self.lyr_overlap_polygon, lyr_vertices
    
    def _create_overlap_feature(self, feat_geom, feat_overlap_geom, feat, lyr_overlap_name) -> None:
        """
        Função auxiliar que cria uma feição de sobreposição.

        @param feat_geom: geometria da feição do input
        @param feat_overlap_geom: geometria da feição em que houve sobreposição
        @param provider: provedor de dados onde a feição de sobreposição será adicionada
        @param feat_attributes: atributos da feição do input
        """
        feat_fields = feat.fields()
        feat_attributes = feat.attributes()
        
        # Cria a feição de sobreposição
        overlap_feat = QgsFeature()

        geom_intersect = feat_geom.intersection(feat_overlap_geom)
        overlap_feat.setGeometry(geom_intersect)

        novo_campo = QgsField('Camada_sobreposicao', QVariant.String)
        feat_fields.append(novo_campo)
        feat_attributes.append(lyr_overlap_name)
        novo_campo = QgsField('logradouro', QVariant.String)
        feat_fields.append(novo_campo)
        feat_attributes.append(feat.attribute('logradouro'))

        overlap_feat.setFields(feat_fields)
        overlap_feat.setAttributes(feat_attributes)

        if geom_intersect.wkbType() in [QgsWkbTypes.Polygon, QgsWkbTypes.MultiPolygon]:
            self.provider_polygon.addFeatures([overlap_feat])

        elif geom_intersect.wkbType() in [QgsWkbTypes.Point, QgsWkbTypes.MultiPoint]:
            self.provider_point.addFeatures([overlap_feat])

        elif geom_intersect.wkbType() in [QgsWkbTypes.LineString, QgsWkbTypes.MultiLineString]:
            self.provider_line.addFeatures([overlap_feat])

        # Atualiza camadas de sobreposição
        self.lyr_overlap_point.commitChanges()
        self.lyr_overlap_line.commitChanges()
        self.lyr_overlap_polygon.commitChanges()
    
    def calcular_soma_areas(self, layer: QgsVectorLayer, epsg: str) -> str:
        soma_geometria = 0.0

        sistema_origem = layer.crs()
        sistema_destino = QgsCoordinateReferenceSystem(f'EPSG:{epsg}')
        transformacao = QgsCoordinateTransform(sistema_origem, sistema_destino, QgsProject.instance())


        for feature in layer.getFeatures():
            geometria = feature.geometry()
            geometria.transform(transformacao)

            if geometria.wkbType() == QgsWkbTypes.LineString or geometria.wkbType() == QgsWkbTypes.MultiLineString:
                soma_geometria += geometria.length()
            elif geometria.wkbType() == QgsWkbTypes.Polygon or geometria.wkbType() == QgsWkbTypes.MultiPolygon:
                soma_geometria += geometria.area()

        soma_geometria_arredondada = round(soma_geometria, 2)
        format_value = f'{soma_geometria_arredondada:_.2f}'
        format_value = format_value.replace('.', ',').replace('_', '.')

        return format_value
    
    def _extract_polygon_vertices(self, layer):
        vertices_layer = QgsVectorLayer('Point?crs={}'.format(layer.crs().authid()), 'vertices', 'memory')
        vertices_layer_fields = QgsFields()
        
        for field in layer.fields():
            vertices_layer_fields.append(field)
        
        vertices_layer_fields.append(QgsField('vertex_id', QVariant.Int))
        vertices_layer_provider = vertices_layer.dataProvider()
        vertices_layer_provider.addAttributes(vertices_layer_fields)
        vertices_layer.updateFields()
        
        vertex_id = 0
        for feature in layer.getFeatures():
            geometry = feature.geometry()
            for point in geometry.vertices():
                new_feature = QgsFeature(vertices_layer_fields)
                new_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(point)))
                new_feature.setAttributes(feature.attributes())
                new_feature['vertex_id'] = vertex_id
                vertex_id += 1
                vertices_layer_provider.addFeature(new_feature)
       
        vertices_layer.setName(NOME_CAMADA_VERTICES)
        return vertices_layer