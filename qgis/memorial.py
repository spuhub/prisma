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

    titulo_memorial_descr = 'MEMORIAL DESCRITIVO'

    ocupante_imovel = layout.itemById('CD_Compl_Ocupante').currentText()
    cpf_cnpj = layout.itemById('CD_Compl_CPF_CNPJ').currentText()
    endereco = layout.itemById('CD_Compl_Logradouro').currentText()
    municipio_uf = layout.itemById('CD_Compl_Municipio').currentText()
    area_total = str(layout.itemById('CD_Compl_Obs2').currentText())
    area_total = area_total[22:-4]
    centroide = str(layout.itemById('CD_Centroide').currentText())
    centroide = centroide.split('Y')
    txt_centroide = centroide[0][:-2] + '; Y' + centroide[1]
    sobreposicao_uniao = str(layout.itemById('CD_Compl_Obs4').currentText())
    sobreposicao_uniao = sobreposicao_uniao[41:-4]
    perimetro_total = '000'

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

    im2 = Image(os.path.join(os.path.dirname(__file__), "static/spu.png"), 35 * mm, 15 * mm)
    im = Image(os.path.join(os.path.dirname(__file__), "static/image_republica.jpeg"), 20 * mm, 20 * mm)
    im.hAlign = 'LEFT'
    im2.hAlign = 'RIGHT'
    im2.vAlign = "TOP"

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(name='titulo_principal', alignment=TA_CENTER, fontName="Times-Roman", textTransform="uppercase",
                       fontSize=11))
    styles.add(ParagraphStyle(name='titulo_secun', alignment=TA_CENTER, fontName="Times-Roman", fontSize=11))

    grupo_titulo = [Paragraph(texto_titulo[0], styles["titulo_principal"]),
                    Paragraph(texto_titulo[1], styles["titulo_secun"]),
                    Paragraph(texto_titulo[2], styles["titulo_secun"]),
                    Paragraph(texto_titulo[3], styles["titulo_secun"]),
                    Paragraph(texto_titulo[4], styles["titulo_secun"])]

    cabecalho_titulo = TablePDF([[im, grupo_titulo, im2]], colWidths=(30 * mm, 130 * mm, 42 * mm), rowHeights=(5 * mm))
    Story.append(cabecalho_titulo)

    Story.append(Spacer(1, 11))
    Story.append(Spacer(1, 11))
    Story.append(Spacer(1, 11))

    styles.add(ParagraphStyle(name='titulo_terc', alignment=TA_CENTER, fontName="Times-Bold", textTransform="uppercase",
                              fontSize=15))

    Story.append(Paragraph(titulo_memorial_descr, styles["titulo_terc"]))

    Story.append(Spacer(1, 11))
    Story.append(Spacer(1, 11))

    dataCabecalho = [["Ocupante do Imóvel: " + ocupante_imovel, "CPF/CNPJ: " + cpf_cnpj]]

    t = TablePDF(dataCabecalho, rowHeights=(5 * mm))
    Story.append(t)

    dataCabecalho = [["Endereço: " + endereco], ["Municipio/UF: " + municipio_uf],
                     ["Área total do Imóvel: " + area_total + " m²", "Perimetro Total (m): " + perimetro_total],
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
    table_1.append(['Vertice', 'Coordenada X', 'Coordenada Y'])

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
                table_2.append(['Vertice', 'Coordenada X', 'Coordenada Y'])
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
    print('tam_table_1: ', tam_table_1)
    print('tam_table_2: ', tam_table_2)

    if tam_table_2 > 0:
        for index, row in enumerate(table_2):
            if index == 0:
                table_1[index].append('')
                table_1[index].append('Vertice')
                table_1[index].append('Coordenada X')
                table_1[index].append('Coordenada Y')
            else:
                table_1[index].append('')
                table_1[index].append(table_2[index][0])
                table_1[index].append(table_2[index][1])
                table_1[index].append(table_2[index][2])

            print(table_1[index])

    return table_1, tam_table_1, tam_table_2

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    # print(gerardoc())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
