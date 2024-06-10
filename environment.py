from qgis.core import QgsWkbTypes

NOME_CAMADA_ENTRADA = 'Feição de Estudo'
NOME_CAMADA_ENTRADA_BUFFER = 'Feição de Estudo (Buffer)'
NOME_CAMADA_SOBREPOSICAO = 'Sobreposição'
NOME_CAMADA_INTERSECAO_PONTO = 'Interseções (Ponto)'
NOME_CAMADA_INTERSECAO_LINHA = 'Interseções (Linha)'
NOME_CAMADA_INTERSECAO_POLIGONO = 'Interseções (Polígono)'
NOME_CAMADA_VERTICES = 'Vértices'

CAMADA_DE_PONTO = ['Point', 'MultiPoint']
CAMADA_DE_LINHA = ['LineString', 'MultiLineString']
CAMADA_DE_POLIGONO = ['Polygon', 'MultiPolygon']

CRS_PADRAO = 4326