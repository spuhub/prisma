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
        email                : guilherme.nascimento@economia.gov.br
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
from qgis.core import QgsFeature, QgsVectorLayer, QgsWkbTypes
from ..utils.lyr_utils import lyr_process

from ..environment import (
    CRS_PADRAO,
    NOME_CAMADA_INTERSECAO_PONTO,
    NOME_CAMADA_INTERSECAO_LINHA,
    NOME_CAMADA_INTERSECAO_POLIGONO
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
        lyr_overlap_point = QgsVectorLayer(f'MultiPoint?crs=epsg:{CRS_PADRAO}', NOME_CAMADA_INTERSECAO_PONTO, 'memory')
        lyr_overlap_line = QgsVectorLayer(f'MultiLineString?crs=epsg:{CRS_PADRAO}', NOME_CAMADA_INTERSECAO_LINHA, 'memory')
        lyr_overlap_polygon = QgsVectorLayer(f'MultiPolygon?crs=epsg:{CRS_PADRAO}', NOME_CAMADA_INTERSECAO_POLIGONO, 'memory')
        
        self.provider_point = lyr_overlap_point.dataProvider()
        self.provider_point.addAttributes(lyr_input.fields())

        self.provider_line = lyr_overlap_line.dataProvider()
        self.provider_line.addAttributes(lyr_input.fields())

        self.provider_polygon = lyr_overlap_polygon.dataProvider()
        self.provider_polygon.addAttributes(lyr_input.fields())

        lyr_overlap_point.updateFields()
        lyr_overlap_line.updateFields()
        lyr_overlap_polygon.updateFields()
                
        dic_overlaps = {}
        lyr_input.startEditing()
        lyr_overlap_point.startEditing()
        lyr_overlap_line.startEditing()
        lyr_overlap_polygon.startEditing()
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
                        self._create_overlap_feature(feat_geom, feat_shp_geom, feat.attributes())
            
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
                        self._create_overlap_feature(feat_geom, feat_db_geom, feat.attributes())
            
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
                        self._create_overlap_feature(feat_geom, feat_wfs_geom, feat.attributes())

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
                        self._create_overlap_feature(feat_geom, feat_req_geom, feat.attributes())

        # Atualiza camada de entrada
        lyr_input.commitChanges()
        # Atualiza camadas de sobreposição
        lyr_overlap_point.commitChanges()
        lyr_overlap_line.commitChanges()
        lyr_overlap_polygon.commitChanges()

        # Adiciona os estilos às camadas de sobreposição
        lyr_overlap_point = lyr_process(lyr_overlap_point, operation_config)
        lyr_overlap_line = lyr_process(lyr_overlap_line, operation_config)
        lyr_overlap_polygon = lyr_process(lyr_overlap_polygon, operation_config)

        # Seta como None a variável caso não tenha nenhuma sobreposição
        if lyr_overlap_point.featureCount() == 0:
            lyr_overlap_point = None
        if lyr_overlap_line.featureCount() == 0:
            lyr_overlap_line = None
        if lyr_overlap_polygon.featureCount() == 0:
            lyr_overlap_polygon = None

        return dic_overlaps, lyr_overlap_point, lyr_overlap_line, lyr_overlap_polygon
    
    def _create_overlap_feature(self, feat_geom, feat_overlap_geom, feat_attributes) -> None:
        """
        Função auxiliar que cria uma feição de sobreposição.

        @param feat_geom: geometria da feição do input
        @param feat_overlap_geom: geometria da feição em que houve sobreposição
        @param provider: provedor de dados onde a feição de sobreposição será adicionada
        @param feat_attributes: atributos da feição do input
        """
        # Cria a feição de sobreposição
        overlap_feat = QgsFeature()

        geom_intersect = feat_geom.intersection(feat_overlap_geom)

        overlap_feat.setGeometry(geom_intersect)
        overlap_feat.setAttributes(feat_attributes)

        if geom_intersect.wkbType() in [QgsWkbTypes.Polygon, QgsWkbTypes.MultiPolygon]:
            self.provider_polygon.addFeatures([overlap_feat])

        elif geom_intersect.wkbType() in [QgsWkbTypes.Point, QgsWkbTypes.MultiPoint]:
            self.provider_point.addFeatures([overlap_feat])

        elif geom_intersect.wkbType() in [QgsWkbTypes.LineString, QgsWkbTypes.MultiLineString]:
            self.provider_line.addFeatures([overlap_feat])
        
        