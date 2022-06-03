import sys
import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidgetItem, QComboBox, QDoubleSpinBox, QCheckBox, QToolButton
from PyQt5.uic import loadUi
from qgis.gui import QgsSymbolButton, QgsColorButton

# from .config_window import ConfigWindow
from .json_tools import JsonTools
from .env_tools import EnvTools
from ..databases.db_connection import DbConnection
import geopandas as gpd
import random
from ..databases.shp_handle import ShpHandle


class ConfigLayers(QtWidgets.QDialog):
    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self, tipo_fonte, id_current_db):
        super(ConfigLayers, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'config_layers.ui'), self)
        self.tipoFonte = tipo_fonte
        self.id_current_db = id_current_db

        # self.config_windows = ConfigWindow()
        self.setings02 = JsonTools()
        self.source_databases = self.setings02.get_config_database()
        # print("O meu deus ",self.source_databases)
        self.source_shp = self.setings02.get_config_shapefile()

        self.objects_vai_usar = []
        self.objects_vai_usar_camada_base = []
        self.objects_tipo_camada_base = []
        self.objects_estilo_linhas = []
        self.objects_cor_linhas = []
        self.objects_espessura_linhas = []
        self.objects_preenchimento = []
        self.objects_cor_preenchimento = []
        self.objects_tables_disponiveis = []
        self.objects_tipo_tables_disponiveis = []
        self.objects_nome_fantasia = []
        self.objects_buffer = []

        self.fill_table()
        self.btn_layer_cancelar.clicked.connect(self.back)
        self.btn_layer_salvar.clicked.connect(self.next)

    def fill_table(self):
        """
        Método responsavel por preencher a tabela com as informações de configuração de cada camda
        @return: void
        """
        if self.tipoFonte == "shp":
            self.fill_table_shp()
        if self.tipoFonte == "bd":
            self.fill_table_bd()

    def create_combobox_line_style(self, id_object):
        """
        Cria e preenche um combobox com os tipos de Linhas.
        @param id_object: um valor para servir de ID do combobox criado.
        @return: void.
        """
        cb = QComboBox()
        cb.setObjectName(id_object)
        cb.addItem("________________________", "solid")
        cb.addItem("-..-..-..-..-..-..-..-..", "dash dot dot")
        cb.addItem("__.__.__.__.__.__.__.__", "dash dot")
        cb.addItem(".......................", "dot")
        cb.addItem("-----------------------", "dash")
        return cb

    def create_comboBox_tipo_camada_base(self, id_object):
        """
        Cria e preenche um combobox com os tipos de camadas bases.
        @param id_object: um valor para servir de ID do combobox criado.
        @return: void.
        """
        cb = QComboBox()
        cb.setObjectName(id_object)
        cb.addItem("LPM Homologada", "lpm_homologada")
        cb.addItem("LTM Homologada", "ltm_homologada")
        cb.addItem("LPM Não Homologada", "lpm_nao_homologada")
        cb.addItem("LTM Não Homologada", "ltm_nao_homologada")
        cb.addItem("Área da União - Homologada", "area_homologada")
        cb.addItem("Área da União - Não Homologada", "area_nao_homologada")
        return cb

    def create_espessura_box(self, id_object, value):

        """
        Cria e preenche um objeto para digitar a espessura da linha.
        @param id_object: um valor para servir de ID do objeto criado.
        @param value: valor padrão do do objeteo.
        @return: void.
        """
        dsb = QDoubleSpinBox()
        dsb.setValue(value)
        dsb.setObjectName(id_object)
        dsb.setSingleStep(0.1)
        return dsb

    def create_buffer_box(self, id_object, value):
        """
        Cria e preenche um SpinBox para digitar o tamanho do buffer.
        @param id_object: um valor para servir de ID do objeto criado.
        @param value: valor padrão do do objeto.
        @return: void.
        """
        dsb = QDoubleSpinBox()
        dsb.setValue(value)
        dsb.setObjectName(id_object)
        dsb.setSingleStep(0.1)
        return dsb

    def create_ComboBox_preenchimento(self, id_object):
        """
        Cria e preenche um combobox com os tipos de preenchimento de camadas bases.
        @param id_object: um valor para servir de ID do combobox criado.
        @return: void.
        """
        cb = QComboBox()
        cb.setObjectName(id_object)
        cb.addItem("solid", "solid")
        return cb

    def create_Color_Select(self, id_object, corDefalt):
        """
        Cria um Color Button para seleção de cores.
        @param id_object:  um valor para servir de ID do objeto criado.
        @param corDefalt: Cor padrão.
        @return:
        """

        co = QgsColorButton()
        co.setObjectName(id_object)
        c = QColor(corDefalt)
        co.setColor(c)
        co.setAllowOpacity(True)
        return co

    def create_usar_check(self, id_object, ischeck):
        """
        Cria Um checkbox para selecionar uma camada para ser usada.
        @param id_object:  um valor para servir de ID do objeto criado.
        @param ischeck: Valor true/false para dizer se vai ficar marcado ou não.
        @return:
        """
        b1 = QCheckBox(" ")
        b1.setChecked(ischeck)
        b1.setObjectName(id_object)
        return b1

    def generate_color(self):
        """
        Gera cores de forma aleatória.
        @return: retorna o valor da cor em Hexadecimal.
        """
        color = ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])]
        return color[0]

    def fill_table_shp(self):

        """
        Método responsável por preencher a tabela com as informações de configuração de cada camada de uma base de dados
        ShapeFile.
        @return: void
        """
        shpHandle = ShpHandle()
        print(self.id_current_db)

        config = self.search_base_shp(self.id_current_db)
        print(config)
        nomereal = config["diretorioLocal"].replace("\\", "/").split("/").pop().split(".")[0]
        #print("caminho", config["diretorioLocal"])

        shp = shpHandle.read_shp_input(config["diretorioLocal"])
        #print("tipe",shp.type)

        self.table_layers.setRowCount(1)
        self.objects_vai_usar.append(self.create_usar_check("check-usar" + str(0), True))
        self.table_layers.setCellWidget(0, 0, self.objects_vai_usar[0]) # Qt::AlignHCenter

        itemCellClass = QTableWidgetItem(nomereal)
        self.table_layers.setItem(0, 1, itemCellClass)

        nome = config["nome"].replace("_", " ").replace("-", " ").title()
        self.objects_nome_fantasia.append(nome)
        itemCellClass = QTableWidgetItem(nome)
        self.table_layers.setItem(0, 2, itemCellClass)

        itemCellClass = QTableWidgetItem(str(shp.type).replace("0", "").replace(" ", ""))
        self.table_layers.setItem(0, 3, itemCellClass)

        #self.objects_vai_usar_camada_base.append(self.create_usar_check("check-camada-base" + str(0), False))
        #self.table_layers.setCellWidget(0, 4, self.objects_vai_usar_camada_base[0])

        #self.objects_tipo_camada_base.append(
         #   self.create_comboBox_tipo_camada_base("tipobase" + "-" + str(0) + "-" + str(5)))
        #self.table_layers.setCellWidget(0, 5, self.objects_tipo_camada_base[0])

        self.objects_estilo_linhas.append(self.create_combobox_line_style("tipolinha" + "-" + str(0) + "-" + str(6)))
        self.table_layers.setCellWidget(0, 4, self.objects_estilo_linhas[0])

        self.objects_cor_linhas.append(self.create_Color_Select("corLinha" + "-" + str(0) + "-" + str(7), "black"))
        self.table_layers.setCellWidget(0, 5, self.objects_cor_linhas[0])

        self.objects_espessura_linhas.append(self.create_espessura_box("espessura" + "-" + str(0) + "-" + str(8),0.25))
        self.table_layers.setCellWidget(0, 6, self.objects_espessura_linhas[0])

        self.objects_preenchimento.append(
            self.create_ComboBox_preenchimento("preenchimento" + "-" + str(0) + "-" + str(9)))
        self.table_layers.setCellWidget(0, 7, self.objects_preenchimento[0])

        self.objects_cor_preenchimento.append(
            self.create_Color_Select("corPreenchimento" + "-" + str(0) + "-" + str(10), self.generate_color()))
        self.table_layers.setCellWidget(0, 8, self.objects_cor_preenchimento[0])

        defaltFaixaProximidade = 0.25
        self.objects_buffer.append(self.create_buffer_box("espessura" + "-" + str(0) + "-" + str(11), defaltFaixaProximidade))
        self.table_layers.setCellWidget(0, 9, self.objects_buffer[0])

        self.btn = QToolButton()
        self.btn.setText("...")
        self.table_layers.setCellWidget(0, 10, self.btn)


    def fill_table_bd(self):

        """
        Método responsável por preencher a tabela com as informações de configuração de cada camada de uma base de dados
        PostgreSQL.
        @return: void
        """
        #print(self.id_current_db)
        idbd = self.id_current_db
        config = self.search_base_pg(self.id_current_db)

        env = EnvTools()
        credenciais = env.get_credentials(idbd)
        conn = DbConnection(config["host"], config["porta"], config["baseDeDados"], credenciais[0], credenciais[1])

        dataTables = conn.GEtAllTypeGeomOFGeomColum("public")
        tabelasGeom = list(dataTables.keys())

        tabelasCamadas = []
        nomeFantasiaTabelasCamadas =[]
        descricaoTabelasCamadas = []
        estiloTabelasCamadas = []
        aproximacao=[]

        if "TabelasDisponiveis" in config:
            tabelasGeom = config["TabelasDisponiveis"]

        if "TipoTabelasDisponiveis" in config:
            dataTables = dict(zip(tabelasGeom, config["TipoTabelasDisponiveis"]))

        if "tabelasCamadas" in config:
            tabelasCamadas = config["tabelasCamadas"]

        if "nomeFantasiaTabelasCamadas" in config:
            nomeFantasiaTabelasCamadas = config["nomeFantasiaTabelasCamadas"]

        if "descricaoTabelasCamadas" in config:
            descricaoTabelasCamadas = config["descricaoTabelasCamadas"]

        if "estiloTabelasCamadas" in config:
            estiloTabelasCamadas = config["estiloTabelasCamadas"]
        if "aproximacao" in config:
            aproximacao = config["aproximacao"]

        self.objects_tables_disponiveis = tabelasGeom
        self.objects_tipo_tables_disponiveis = dataTables.values()
        nb_row = len(tabelasGeom)

        self.table_layers.setRowCount(nb_row)
        # itemCellClass = QTableWidgetItem(classe)

        for i in range(nb_row):

            if tabelasGeom[i] in tabelasCamadas:
                self.objects_vai_usar.append(self.create_usar_check("check-usar" + str(i), True))
            else:
                self.objects_vai_usar.append(self.create_usar_check("check-usar" + str(i), False))

            self.table_layers.setCellWidget(i, 0, self.objects_vai_usar[i])

            itemCellClass = QTableWidgetItem(tabelasGeom[i])
            self.table_layers.setItem(i, 1, itemCellClass)

            if tabelasGeom[i] in tabelasCamadas:
                itemidex = tabelasCamadas.index(tabelasGeom[i])
                nome = tabelasCamadas[itemidex].replace("_", " ").replace("-", " ").title()
                self.objects_nome_fantasia.append(nome)
                itemCellClass = QTableWidgetItem(nome)

            else:
                nome = tabelasGeom[i].replace("_", " ").replace("-", " ").title()
                self.objects_nome_fantasia.append(nome)
                itemCellClass = QTableWidgetItem(nome)

            self.table_layers.setItem(i, 2, itemCellClass)


            itemCellClass = QTableWidgetItem(dataTables[tabelasGeom[i]])
            self.table_layers.setItem(i, 3, itemCellClass)

            #self.objects_vai_usar_camada_base.append(self.create_usar_check("check-camada-base" + str(i), False))
            #self.table_layers.setCellWidget(i, 4, self.objects_vai_usar_camada_base[i])


            #self.objects_tipo_camada_base.append(self.create_comboBox_tipo_camada_base("tipobase" + "-" + str(i) + "-" + str(5)))
            #self.table_layers.setCellWidget(i, 5, self.objects_tipo_camada_base[i])

            style = {}

            if tabelasGeom[i] in tabelasCamadas:
                itemidex = tabelasCamadas.index(tabelasGeom[i])
                style = estiloTabelasCamadas[itemidex]


            self.objects_estilo_linhas.append(self.create_combobox_line_style("tipolinha" + "-" + str(i) + "-" + str(6)))

            if "line_style" in style:
                indexQcombo = self.objects_estilo_linhas[i].findData("line_style")
                self.objects_estilo_linhas[i].setCurrentIndex(indexQcombo)

            self.table_layers.setCellWidget(i, 4, self.objects_estilo_linhas[i])

            lineColor = "black"
            if "line_color" in style:
                lineColor = style["line_color"]

            self.objects_cor_linhas.append(self.create_Color_Select("corLinha" + "-" + str(i) + "-" + str(7),lineColor))
            self.table_layers.setCellWidget(i, 5, self.objects_cor_linhas[i])

            espeLine = 0.25

            if "width_border" in style:
                espeLine = float(style["width_border"])

            self.objects_espessura_linhas.append(self.create_espessura_box("espessura" + "-" + str(i) + "-" + str(8), espeLine))
            self.table_layers.setCellWidget(i, 6, self.objects_espessura_linhas[i])


            self.objects_preenchimento.append(self.create_ComboBox_preenchimento("preenchimento" + "-" + str(i) + "-" + str(9)))
            self.table_layers.setCellWidget(i, 7, self.objects_preenchimento[i])

            fillColor = self.generate_color()

            if "color" in style:
                fillColor = style["color"]
            self.objects_cor_preenchimento.append(self.create_Color_Select("corPreenchimento" + "-" + str(i) + "-" + str(10), fillColor))
            self.table_layers.setCellWidget(i, 8, self.objects_cor_preenchimento[i])

            defalt_aproximacao = 0.25

            if tabelasGeom[i] in tabelasCamadas:
                itemidex = tabelasCamadas.index(tabelasGeom[i])
                print("itemindex",itemidex)
                if(len(aproximacao) !=0):
                    defalt_aproximacao = aproximacao[itemidex]

            self.objects_buffer.append(self.create_buffer_box("espessura" + "-" + str(i) + "-" + str(11), defalt_aproximacao))
            self.table_layers.setCellWidget(i, 9, self.objects_buffer[i])


    def save_base_pg(self):
        """
        Método responsável por Gravar as configurações das camadas de uma base de dados PostgreSQL
        @return: void
        """
        idbd = self.id_current_db
        config = self.search_base_pg(self.id_current_db)
        print(type(config))

        config["TabelasDisponiveis"] = self.objects_tables_disponiveis
        config["TipoTabelasDisponiveis"] = list(self.objects_tipo_tables_disponiveis)
        print("OIIIII", config["TipoTabelasDisponiveis"])
        aux = []
        for i in range(len(self.objects_tables_disponiveis)):
            if self.objects_vai_usar[i].checkState():
                aux.append(self.objects_tables_disponiveis[i])

        config["tabelasCamadas"] = aux

        aux=[]

        for i in range(len(self.objects_tables_disponiveis)):
            if self.objects_vai_usar[i].checkState():
                aux.append(self.objects_buffer[i].value())

        config["aproximacao"] = aux
        print("Aproximacao aqui: ",config["aproximacao"])

        aux = []

        for i in range(len(self.objects_tables_disponiveis)):
            if self.objects_vai_usar[i].checkState():
                aux.append(self.objects_nome_fantasia[i])

        config["nomeFantasiaTabelasCamadas"] = aux

        aux = []

        for i in range(len(self.objects_tables_disponiveis)):
            if self.objects_vai_usar[i].checkState():
                aux.append("Builder")

        config["descricaoTabelasCamadas"] = aux

        aux = []
        for i in range(len(self.objects_tables_disponiveis)):
            if self.objects_vai_usar[i].checkState():
                c = {"line_style": self.objects_estilo_linhas[i].currentData(),
                "line_color": self.objects_cor_linhas[i].color().name(),
                "width_border": str(self.objects_espessura_linhas[i].value()),
                "style": self.objects_preenchimento[i].currentData(),
                "color": self.objects_cor_preenchimento[i].color().name()}
                aux.append(c)

        config["estiloTabelasCamadas"] = aux

        print(config)
        self.setings02.edit_database(self.id_current_db,config)

    def save_base_shp(self):
        """
        Método responsável por Gravar as configurações das camadas de uma base de dados Shapefile
        @return: void.
        """
        idbd = self.id_current_db
        print ("Currente-shp2223: ",  idbd)
        config = self.search_base_shp(self.id_current_db)

        config["nomeFantasiaCamada"] = self.objects_nome_fantasia[0]

        c = {"line_style": self.objects_estilo_linhas[0].currentData(),
             "line_color": self.objects_cor_linhas[0].color().name(),
             "width_border": str(self.objects_espessura_linhas[0].value()),
             "style": self.objects_preenchimento[0].currentData(),
             "color": self.objects_cor_preenchimento[0].color().name()}

        config["estiloCamadas"] = [c]

        config["aproximacao"] = [self.objects_buffer[0].value()]


        self.setings02.edit_database(idbd,config)

    def search_base_pg(self, id_base):
        config = {}
        for item in self.source_databases:
            if item["id"] == id_base:
                config = item

        return config

    def search_base_shp(self, id_base):
        config = {}
        for item in self.source_shp:
            if item["id"] == id_base:
                config = item

        return config

    def search_index_base_shp(self, id_base):
        idex = 0
        for item in self.source_shp:
            if item["id"] != id_base:
                idex = idex + 1

        return idex

    def search_index_base_pg(self, id_base):
        idex = 0
        # cont=0
        for item in self.source_databases:
            if item["id"] != id_base:
                idex = idex + 1

        return idex

    def back(self):
        self.hide()
        self.back_window.emit()

    def next(self):
        # print(self.testefill.symbol)
        #print(self.bt.color().name())

        if self.tipoFonte == "shp":
            self.save_base_shp()
        if self.tipoFonte == "bd":
            self.save_base_pg()

        self.hide()
        self.continue_window.emit()

    def pr(self):
        print(self.testefill.symbol)
