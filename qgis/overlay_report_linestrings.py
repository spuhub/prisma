# -*- coding: utf-8 -*-
import os

from qgis.PyQt.QtWidgets import QApplication
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsRasterLayer, QgsVectorLayer, QgsFillSymbol, \
    QgsLineSymbol, QgsMarkerSymbol, QgsRectangle, QgsMapSettings, QgsLayoutSize, QgsUnitTypes, QgsLayoutExporter, \
    QgsPrintLayout, QgsReadWriteContext, QgsPalLayerSettings, QgsTextFormat, QgsVectorLayerSimpleLabeling
from qgis.PyQt.QtXml import QDomDocument
from qgis.utils import iface
from PyQt5.QtCore import Qt

from ..utils.utils import Utils
from ..settings.env_tools import EnvTools
from ..analysis.overlay_analysis import OverlayAnalisys
from .memorial import gerardoc

import geopandas as gpd
from shapely.geometry import Polygon, Point, LineString
from PyPDF2 import PdfFileReader, PdfFileMerger
from datetime import datetime


class OverlayReportLinestrings():

    def __init__(self):
        self.layout = QgsProject.instance().layoutManager().layoutByName("Relatorio_FolhaA4_Retrato")



    def handle_overlay_report(self, gdf_input, operation_config, time, base_type, index_1, index_2):
        camada_sem=""
        camada_com=""
        camada_sem, camada_com = self.overlay_shapefile(gdf_input, operation_config, camada_sem, camada_com)
        camada_sem, camada_com = self.overlay_wfs(gdf_input, operation_config, camada_sem, camada_com)
        camada_sem, camada_com = self.overlay_database(gdf_input, operation_config, camada_sem, camada_com)
        camada_sem, camada_com = self.overlay_required(gdf_input, operation_config, camada_sem, camada_com)
        com = self.layout.itemById('CD_Com_Sobreposicao_Texto')
        sem = self.layout.itemById('CD_Sem_Sobreposicao_Texto')
        com.setText(camada_com)
        sem.setText(camada_sem)

        id_0 = self.layout.itemById('CD_Compl_id')
        if "id_atlas" in gdf_input.columns:
            id = gdf_input.iloc[0]["id_atlas"]
            id_0.setText(id)
        else:
            id_0.setText("Não informado.")

        municipio_0 = self.layout.itemById('CD_Compl_Municipio')
        if "municipio" in gdf_input.columns:
            municipio = gdf_input.iloc[0]["municipio"]
            municipio_0.setText(municipio)
        else:
            municipio_0.setText("Não informado.")

        uf_0 = self.layout.itemById('CD_Compl_UF')
        if "uf" in gdf_input.columns:
            uf = gdf_input.iloc[0]["uf"]
            uf_0.setText(uf)
        else:
            uf_0.setText("Não informado.")

        ocupante_0 = self.layout.itemById('CD_Compl_Ocupante')
        if "ocupante" in gdf_input.columns:
            ocupante = gdf_input.iloc[0]["ocupante"]
            ocupante_0.setText(ocupante)
        else:
            ocupante_0.setText("Não informado.")

        cpf_cnpj_0 = self.layout.itemById('CD_Compl_CPF_CNPJ')
        if "cpf_cnpj" in gdf_input.columns:
            cpf_cnpj = str(gdf_input.iloc[0]["cpf_cnpj"])
            cpf_cnpj_0.setText(cpf_cnpj)
        else:
            cpf_cnpj_0.setText("Não informado.")

        logradouro_0 = self.layout.itemById('CD_Compl_Logradouro')
        if "logradouro" in gdf_input.columns:
            logradouro = gdf_input.iloc[0]["logradouro"]
            logradouro_0.setText(logradouro)
        else:
            logradouro_0.setText("Não informado.")

        bairro_0 = self.layout.itemById('CD_Compl_Bairro')
        if "bairro" in gdf_input.columns:
            bairro = gdf_input.iloc[0]["bairro"]
            bairro_0.setText(bairro)
        else:
            bairro_0.setText("Não informado.")

        et = EnvTools()
        headers = et.get_report_hearder()

        ministerio = self.layout.itemById('CD_Cabecalho_Ministerio')
        ministerio.setText(headers['ministerio'])

        sec_esp = self.layout.itemById('CD_Cabecalho_Secretaria_Esp')
        sec_esp.setText(headers['secretariaEspecial'])

        secretaria = self.layout.itemById('CD_Cabecalho_Secretaria')
        secretaria.setText(headers['secretaria'])

        superintendencia = self.layout.itemById('CD_Cabecalho_Superintendencia')
        superintendencia.setText(headers['superintendencia'])

        setor = self.layout.itemById('CD_Cabecalho_Setor')
        setor.setText(headers['setor'])

        self.export_pdf(gdf_input, operation_config, time, base_type, index_1, index_2)


    def overlay_shapefile(self, gdf_input, operation_config, camada_sem, camada_com):
        for i in operation_config['operation_config']['shp']:
            if type(i['nomeFantasiaCamada']) is list:
                i['nomeFantasiaCamada'] = i['nomeFantasiaCamada'][0]
            for index, row in gdf_input.iterrows():
                print("TESTE: ", i['nomeFantasiaCamada'], gdf_input.iloc[index][i['nomeFantasiaCamada']])
                print("TESTE2: --------")

            for rowIndex, row in gdf_input.iterrows():
                if str(i['nomeFantasiaCamada']) in gdf_input.columns and gdf_input.iloc[rowIndex][str(i['nomeFantasiaCamada'])] == True:
                    camada_com+=i["nomeFantasiaCamada"]+"; "
                else:
                    camada_sem+=i["nomeFantasiaCamada"]+"; "
        return camada_sem, camada_com

    def overlay_wfs(self, gdf_input, operation_config, camada_sem, camada_com):
        for i in operation_config['operation_config']['wfs']:
            if type(i['nomeFantasiaTabelasCamadas']) is list:
                i['nomeFantasiaTabelasCamadas'] = i['nomeFantasiaTabelasCamadas'][0]

            for rowIndex, row in gdf_input.iterrows():
                if str(i['nomeFantasiaTabelasCamadas']) in gdf_input.columns and gdf_input.iloc[rowIndex][str(i['nomeFantasiaTabelasCamadas'])] > 0:
                    camada_com+=i["nomeFantasiaTabelasCamadas"]+"; "
                else:
                    camada_sem+=i["nomeFantasiaTabelasCamadas"]+"; "
        return camada_sem, camada_com

    def overlay_database(self, gdf_input, operation_config, camada_sem, camada_com):
        for bd in operation_config['operation_config']['pg']:
            for layer in bd['nomeFantasiaTabelasCamadas']:
                for rowIndex, row in gdf_input.iterrows():
                    if str(str(layer)) in gdf_input.columns and gdf_input.iloc[rowIndex][str(layer)] == True:
                        camada_com += layer + "; "
                    else:
                        camada_sem += layer + "; "
        return camada_sem, camada_com

    def overlay_required(self, gdf_input, operation_config, camada_sem, camada_com):
        for i in operation_config['operation_config']['obrigatorio']:

            for rowIndex, row in gdf_input.iterrows():
                if i['tipo'] == 'shp':
                    if type(i['nomeFantasiaCamada']) is list:
                        if i['nomeFantasiaCamada'][0] == "Área Homologada" or i['nomeFantasiaCamada'][0] == "Área Não Homologada":
                            if str(i['nomeFantasiaCamada'][0]) in gdf_input and gdf_input.iloc[rowIndex][str(i['nomeFantasiaCamada'][0])] > 0:
                                camada_com += i['nomeFantasiaCamada'][0] + "; "
                            else:
                                camada_sem += i['nomeFantasiaCamada'][0] + "; "
                        else:
                            if str(i['nomeFantasiaCamada'][0]) in gdf_input and gdf_input.iloc[rowIndex][str(i['nomeFantasiaCamada'][0])] == True:
                                camada_com += i['nomeFantasiaCamada'][0] + "; "
                            else:
                                camada_sem += i['nomeFantasiaCamada'][0] + "; "

                    else:
                        if i['nomeFantasiaCamada'] == "Área Homologada" or i[
                            'nomeFantasiaCamada'] == "Área Não Homologada":
                            if str(i['nomeFantasiaCamada']) in gdf_input and gdf_input.iloc[rowIndex][str(i['nomeFantasiaCamada'])] > 0:
                                camada_com += i['nomeFantasiaCamada'] + "; "
                            else:
                                camada_sem += i['nomeFantasiaCamada'] + "; "
                        else:
                            if str(i['nomeFantasiaCamada']) in gdf_input and gdf_input.iloc[rowIndex][str(i['nomeFantasiaCamada'])] == True:
                                camada_com += i['nomeFantasiaCamada'] + "; "
                            else:
                                camada_sem += i['nomeFantasiaCamada'] + "; "
                else:
                    if type(i['nomeFantasiaTabelasCamadas']) is list:
                        if i['nomeFantasiaTabelasCamadas'][0] == "Área Homologada" or i['nomeFantasiaTabelasCamadas'][
                            0] == "Área Não Homologada":
                            if str(i['nomeFantasiaTabelasCamadas'][0]) in gdf_input and gdf_input.iloc[rowIndex][str(i['nomeFantasiaTabelasCamadas'][0])] > 0:
                                camada_com += i['nomeFantasiaTabelasCamadas'][0] + "; "
                            else:
                                camada_sem += i['nomeFantasiaTabelasCamadas'][0] + "; "
                        else:
                            if str(i['nomeFantasiaTabelasCamadas'][0]) in gdf_input and gdf_input.iloc[rowIndex][str(i['nomeFantasiaTabelasCamadas'][0])] == True:
                                camada_com += i['nomeFantasiaTabelasCamadas'][0] + "; "
                            else:
                                camada_sem += i['nomeFantasiaTabelasCamadas'][0] + "; "
                    else:
                        if i['nomeFantasiaTabelasCamadas'] == "Área Homologada" or i['nomeFantasiaTabelasCamadas'] == "Área Não Homologada":
                            if str(i['nomeFantasiaTabelasCamadas']) in gdf_input and gdf_input.iloc[rowIndex][str(i['nomeFantasiaTabelasCamadas'])] > 0:
                                camada_com += i['nomeFantasiaTabelasCamadas'] + "; "
                            else:
                                camada_sem += i['nomeFantasiaTabelasCamadas'] + "; "
                        else:
                            if str(i['nomeFantasiaTabelasCamadas']) in gdf_input and gdf_input.iloc[rowIndex][str(i['nomeFantasiaTabelasCamadas'])] == True:
                                camada_com += i['nomeFantasiaTabelasCamadas'] + "; "
                            else:
                                camada_sem += i['nomeFantasiaTabelasCamadas'] + "; "

        return camada_sem, camada_com


    def export_pdf(self, feature_input_gdp, operation_config, time, base_type, index_1, index_2):
        """
        Função responsável carregar o layout de impressão e por gerar os arquivos PDF.

        @keyword feature_input_gdp: Feição de input comparada
        @keyword index_1: Variável utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar informções como estilização ou nome da camada.
        @keyword index_2: Variável utilizada para pegar dados armazenados no arquivo Json, exemplo: pegar informções como estilização ou nome da camada.
        """

        if 'logradouro' not in feature_input_gdp:
            feature_input_gdp['logradouro'] = "Ponto por Endereço ou Coordenada"

        if index_1 == None and index_2 == None:
            pdf_name = str(feature_input_gdp.iloc[0]['logradouro']) + '_' + str(time) + '_AreasObrigatorias.pdf'
        elif base_type == "shp":
            pdf_name = str(feature_input_gdp.iloc[0]['logradouro']) + '_' + str(time) + '_' + str(
                operation_config['operation_config']['shp'][index_1]['nomeFantasiaCamada']) + '.pdf'

        elif base_type == "wfs":
            pdf_name = str(feature_input_gdp.iloc[0]['logradouro']) + '_' + str(time) + '_' + str(
                operation_config['operation_config']['wfs'][index_1]['nomeFantasiaTabelasCamadas']) + '.pdf'

        else:
            pdf_name = str(feature_input_gdp.iloc[0]['logradouro']) + '_' + str(time) + '_' + str(
                operation_config['operation_config']['pg'][index_1]['nomeFantasiaTabelasCamadas'][
                    index_2]) + '.pdf'

        pdf_path = os.path.join(operation_config['path_output'], pdf_name)

        atlas = self.layout.atlas()
        """Armazena o atlas do layout de impressão carregado no projeto."""
        map_atlas = atlas.layout()
        pdf_settings = QgsLayoutExporter(map_atlas).PdfExportSettings()
        pdf_settings.dpi = 300

        pdf_settings.rasterizeWholeImage = True
        exporter = QgsLayoutExporter(self.layout)
        exporter.exportToPdf(pdf_path,
                                          settings=pdf_settings)

        self.merge_pdf(operation_config, pdf_name)


    def merge_pdf(self, operation_config, pdf_name):
        pdf_name = "_".join(pdf_name.split("_", 3)[:3])
        print(pdf_name)
        # files_dir = os.path.normpath(files_dir)
        # print(files_dir)
        pdf_files = [f for f in os.listdir(operation_config['path_output']) if f.startswith(pdf_name) and f.endswith(".pdf")]
        pdf_files = pdf_files[::-1]

        merger = PdfFileMerger()

        for filename in pdf_files:
            merger.append(PdfFileReader(os.path.join(operation_config['path_output'], filename), "rb"))

        merger.write(os.path.join(operation_config['path_output'], pdf_name + ".pdf"))

        for filename in os.listdir(operation_config['path_output']):
            if pdf_name in filename and filename.count("_") > 2:
                os.remove(operation_config['path_output'] + "/" + filename)

