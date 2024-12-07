## 
## ESSE ARQUIVO NÃO ESTÁ SENDO UTILIZADO NO MOMENTO
## FUNCIONALIDADE JÁ IMPLEMENTADA PARA GERAR MEMORIAL DE VÉRTICES DOS POLÍGONOS DE ENTRADA
##

from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table as TablePDF, TableStyle
from datetime import date
from reportlab.lib.units import mm
from ..settings.env_tools import EnvTools
import os
import geopandas as gpd
import numpy as np
import math

def gerardoc(gdf_input, gdf_vertices, pdf_name, pdf_path, layout, operation_config):
    Story = []

    et = EnvTools()
    headers = et.get_report_hearder()

    texto_titulo = [str(headers['ministerio']) + '\n', str(headers['secretariaEspecial']) + '\n',
                    str(headers['secretaria']),
                    str(headers['superintendencia']),
                    str(headers['setor'])]

    titulo_memorial_descr = 'MEMORIAL SINTÉTICO DE VÉRTICES'

    ocupante_imovel = layout.itemById('CD_Compl_Ocupante').currentText()
    cpf_cnpj = layout.itemById('CD_Compl_CPF_CNPJ').currentText()
    endereco = layout.itemById('CD_Compl_Logradouro').currentText()
    municipio_uf = layout.itemById('CD_Compl_Municipio').currentText()
    
    area_total: str = "0,00"
    if 'areaLote' in gdf_input:
        format_value = f'{gdf_input["areaLote"][0]:_.2f}'
        format_value = format_value.replace('.', ',').replace('_', '.')
        area_total = str(format_value)
    

    centroide = str(layout.itemById('CD_Centroide').currentText())
    centroide = centroide.split('Y')
    txt_centroide = centroide[0][:-1] + '; Y' + centroide[1]

    sobreposicao_uniao: str = "0,00"
    if 'Área Homologada' in gdf_input:
            format_value = f'{gdf_input.iloc[0]["Área Homologada"]:_.2f}'
            format_value = format_value.replace('.', ',').replace('_', '.')
            sobreposicao_uniao = str(format_value)

    titulo_descricao = "descrição"

    utm_zone = str(layout.itemById('CD_SRC').currentText())
    utm_zone = utm_zone[36:]

    Descrição = "Inicia-se a descrição dessa poligonal fechada no vértice 0, " \
                "conforme tabela abaixo, onde todas as coordenadas descritas estão " \
                "georreferenciadas ao Sistema Geodésico Brasileiro, projetadas no sistema " \
                "UTM, Fuso " + utm_zone + " e tendo como Datum SIRGAS 2000, sendo: "

    pdf_path = pdf_path.replace(".pdf", "_Memorial.pdf")

    # rodape_cidade = "Florianópolis/SC,"

    local_data = "Florianopolis/SC, 13.09.2021"
    # rodape = "Superintendência do patrimônio da União  em Santa Catarina"

    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=10 * mm, leftMargin=20 * mm, topMargin=30 * mm,
                            bottomMargin=35)

    image_brasao = Image(os.path.join(os.path.dirname(__file__), "static/Brasao_Oficial_Colorido.png"), 20 * mm, 20 * mm)
    image_brasao.hAlign = 'LEFT'

    image_spu = Image(os.path.join(os.path.dirname(__file__), "static/spu.png"), 25 * mm, 20 * mm)
    image_spu.hAlign = 'RIGHT'

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='titulo_principal', fontName="Times-Roman", fontSize=11))
    styles.add(ParagraphStyle(name='titulo_secun', fontName="Times-Roman", fontSize=11))

    grupo_titulo = [Paragraph(texto_titulo[0], styles["titulo_principal"]),
                    Paragraph(texto_titulo[1], styles["titulo_secun"]),
                    Paragraph(texto_titulo[2], styles["titulo_secun"]),
                    Paragraph(texto_titulo[3], styles["titulo_secun"]),
                    Paragraph(texto_titulo[4], styles["titulo_secun"])]

    cabecalho_titulo = TablePDF([[image_brasao, grupo_titulo, image_spu]], colWidths=(30 * mm, 125 * mm, 35 * mm), rowHeights=(5 * mm))
    Story.append(cabecalho_titulo)

    Story.append(Spacer(1, 11))
    Story.append(Spacer(1, 11))
    Story.append(Spacer(1, 11))

    styles.add(ParagraphStyle(name='titulo_terc', alignment=TA_CENTER, fontName="Times-Bold", textTransform="uppercase",
                              fontSize=15, backColor=(0.8, 0.8, 0.8), leading=17))

    Story.append(Paragraph(titulo_memorial_descr, styles["titulo_terc"]))

    Story.append(Spacer(1, 11))
    Story.append(Spacer(1, 11))

    dataCabecalho = [["Ocupante do Imóvel: " + ocupante_imovel, "CPF/CNPJ: " + cpf_cnpj]]

    t = TablePDF(dataCabecalho, colWidths=(76 * mm, 100 * mm), rowHeights=(5 * mm))
    Story.append(t)

    dataCabecalho = [["Endereço: " + endereco], ["Municipio/UF: " + municipio_uf],
                     ["Área total do Imóvel: " + area_total + " m²"],
                     ["Sobreposição Área da União: " + sobreposicao_uniao + " m²", "Centroide: " + txt_centroide]]
    t = TablePDF(dataCabecalho, colWidths=(76 * mm, 100 * mm), rowHeights=4 * [5 * mm])
    Story.append(t)

    Story.append(Spacer(1, 11))
    Story.append(Spacer(1, 11))

    Story.append(Paragraph(titulo_descricao, styles["titulo_terc"]))

    Story.append(Spacer(1, 11))
    Story.append(Spacer(1, 11))

    styles.add(ParagraphStyle(name='descricao', alignment=TA_JUSTIFY, fontName="Times-Roman"))
    ptext = '<font size=12>%s</font>' % Descrição
    Story.append(Paragraph(ptext, styles["descricao"]))
    Story.append(Spacer(1, 11))
    Story.append(Spacer(1, 11))

    table_1, tam_table_1, tam_table_2 = handle_table(gdf_vertices)

    if tam_table_2 > 0:
        t_1 = TablePDF(table_1, rowHeights=tam_table_1 * [5 * mm])

        t_1.setStyle(TableStyle([('BOX', (0, 0), (0, 2), 0, colors.black),
                                 ('GRID', (0, 0), (2, (tam_table_1-1)), 0.5, colors.black),
                                 ('GRID', (4, 0), (6, (tam_table_2-1)), 0.5, colors.black),
                                 ('FONT', (1, 0), (6, tam_table_1), 'Times-Roman', 10.5),
                                 ('FONT', (0, 0), (6, 0), 'Times-Bold', 10.5),
                                 ('ALIGN', (0, 0), (6, 0), 'CENTER')]))

        Story.append(t_1)
    else:
        t_1 = TablePDF(table_1, rowHeights=tam_table_1 * [5 * mm])

        t_1.setStyle(TableStyle([('ALIGN', (1, 0), (0, tam_table_1), 'LEFT'),
                                 ('ALIGN', (1, 1), (2, tam_table_1), 'RIGHT'),
                                 ('BOX',(0,0),(0,2),0,colors.black),
                                 ('GRID', (0, 0), (2, tam_table_1), 0.5, colors.black),
                                 ('FONT', (1, 0), (2, tam_table_1), 'Times-Roman', 10.5),
                                 ('FONT', (0, 0), (2, 0), 'Times-Bold', 10.5),
                                 ('ALIGN', (0, 0), (2, 0), 'CENTER')]))

        Story.append(t_1)

    Story.append(Spacer(1, 11))
    Story.append(Spacer(1, 11))
    Story.append(Spacer(1, 11))
    Story.append(Spacer(1, 11))

    styles.add(ParagraphStyle(name='data', alignment=TA_RIGHT, fontName="Times-Roman"))
    Story.append(Paragraph(local_data, styles["data"]))

    doc.build(Story)

def handle_table(gdf_vertices):
    table_1 = []
    table_2 = []
    table_1.append(['Vertice', 'X (E)', 'Y (N)'])

    add_table_1 = True
    count = 0
    for index, row in gdf_vertices.iterrows():
        # Formata valor da coordenada X
        format_value = f'{row["coord_x"]:_.2f}'
        format_value = format_value.replace('.', ',').replace('_', '.')
        coord_x = str(format_value)

        # Formata valor da cooredana Y
        format_value = f'{row["coord_y"]:_.2f}'
        format_value = format_value.replace('.', ',').replace('_', '.')
        coord_y = str(format_value)

        aux = [index, coord_x, coord_y]

        if index <= 25:
            table_1.append(aux)
        elif index >= 26 and index <= 51:
            if index == 26:
                table_2.append(['Vertice', 'X (E)', 'Y (N)'])
            table_2.append(aux)
        elif index >= 52:
            if (count % 46) == 0 and count != 0:
                add_table_1 = not add_table_1

            if add_table_1:
                table_1.append(aux)
            else:
                table_2.append(aux)

            count += 1

    tam_table_1 = len(table_1)
    tam_table_2 = len(table_2)

    if tam_table_2 > 0:
        for index, row in enumerate(table_2):
            if index == 0:
                table_1[index].append('')
                table_1[index].append('Vertice')
                table_1[index].append('X (E)')
                table_1[index].append('Y (N)')
            else:
                table_1[index].append('')
                table_1[index].append(table_2[index][0])
                table_1[index].append(table_2[index][1])
                table_1[index].append(table_2[index][2])

    return table_1, tam_table_1, tam_table_2

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    # print(gerardoc())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
