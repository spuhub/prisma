import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidgetItem, QDoubleSpinBox, QCheckBox, QToolButton
from PyQt5.uic import loadUi
from qgis.gui import QgsColorButton, QgsFileWidget

# from .config_window import ConfigWindow
from .json_tools import JsonTools
from .env_tools import EnvTools
from ..databases.db_connection import DbConnection
import random
from .layer_infor import LayerInfor


class  ConfigLayers(QtWidgets.QDialog):
    """
    Classe responsável por gerenciar a configuração de camadas.

    Permite ao usuário selecionar tabelas ou shapefiles, definir propriedades como 
    buffers e estilos, e salvar as configurações. É utilizada como parte do fluxo 
    de configuração do PRISMA.

    Attributes:
        back_window (pyqtSignal): Sinal emitido ao voltar para a janela anterior.
        continue_window (pyqtSignal): Sinal emitido ao avançar para a próxima janela.
    """
    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self, tipo_fonte, id_current_db, login, senha):
        """
        Inicializa a interface de configuração de camadas.

        Args:
            tipo_fonte (str): Tipo da fonte de dados ('bd' para banco de dados ou 'shp' para shapefiles).
            id_current_db (int): Identificador da base de dados a ser configurada.
            login (str): Login do banco de dados.
            senha (str): Senha do banco de dados.
        """
        super(ConfigLayers, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'config_layers.ui'), self)
        self.tipoFonte = tipo_fonte
        self.id_current_db = id_current_db
        self.login = login
        self.senha = senha

        # self.config_windows = ConfigWindow()
        self.setings02 = JsonTools()
        self.source_databases = self.setings02.get_config_database()
        # print("O meu deus ",self.source_databases)
        self.source_shp = self.setings02.get_config_shapefile()

        self.objects_vai_usar = []
        self.objects_vai_usar_camada_base = []
        self.objects_tipo_camada_base = []
        self.objects_tables_disponiveis = []
        self.objects_tipo_tables_disponiveis = []
        self.objects_nome_fantasia = []
        self.objects_buffer = []
        self.objects_file_style = []
        self.objects_button_mais_infor = []

        self.fill_table()
        self.btn_layer_cancelar.clicked.connect(self.back)
        self.btn_layer_salvar.clicked.connect(self.next)

    def fill_table(self):
        """
        Método responsavel por preencher a tabela com as informações de configuração de cada camda
        """
        # if self.tipoFonte == "shp":
        #     self.fill_table_shp()
        if self.tipoFonte == "bd":
            self.fill_table_bd()


    def create_buffer_box(self, id_object, value):
        """
        Cria e configura um spinbox para entrada do tamanho do buffer.

        Args:
            id_object (str): Identificador único do spinbox.
            value (float): Valor inicial do buffer.

        Returns:
            QDoubleSpinBox: Spinbox configurado.
        """
        dsb = QDoubleSpinBox()
        dsb.setValue(value)
        dsb.setObjectName(id_object)
        dsb.setSingleStep(0.1)
        return dsb


    def create_Color_Select(self, id_object, corDefalt):
        """
        Cria um botão de seleção de cor.

        Args:
            id_object (str): Identificador único do botão.
            corDefalt (str): Cor inicial no formato hexadecimal.

        Returns:
            QgsColorButton: Botão de seleção de cor.
        """
        co = QgsColorButton()
        co.setObjectName(id_object)
        c = QColor(corDefalt)
        co.setColor(c)
        co.setAllowOpacity(True)
        return co

    def create_usar_check(self, id_object, ischeck):
        """
        Cria um checkbox para selecionar se uma camada será utilizada.

        Args:
            id_object (str): Identificador único do checkbox.
            ischeck (bool): Define se o checkbox está marcado.

        Returns:
            QCheckBox: Checkbox configurado.
        """
        b1 = QCheckBox(" ")
        b1.setChecked(ischeck)
        b1.setObjectName(id_object)
        return b1

    def create_filePath(self, id_object):
        """
        Cria um widget de seleção de arquivo.

        Args:
            id_object (str): Identificador único do widget.

        Returns:
            QgsFileWidget: Widget de seleção de arquivo.
        """

        btn = QgsFileWidget()
        btn.setObjectName(id_object)
        return btn

    def create_button_mais_inf(self, id_object):
        """
        Cria um botão para abrir informações adicionais sobre a camada.

        Args:
            id_object (str): Identificador único do botão.

        Returns:
            QToolButton: Botão configurado.
        """
        btn = QToolButton()
        btn.setObjectName(id_object)
        btn.setText("...")
        return btn

    def generate_color(self):
        """
        Gera uma cor aleatória em formato hexadecimal.

        Returns:
            str: Cor gerada em formato hexadecimal.
        """
        color = ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])]
        return color[0]


    def fill_table_bd(self):
        """
        Método responsável por preencher a tabela com as informações de configuração de cada camada de uma base de dados
        PostgreSQL.
        """
        print(self.id_current_db)
        idbd = self.id_current_db
        config = self.search_base_pg(self.id_current_db)

        env = EnvTools()
        credenciais = env.get_credentials(idbd)
        print("credenciais config layer",credenciais)
        conn = DbConnection(config["host"], config["porta"], config["baseDeDados"], self.login, self.senha)

        dataTables = conn.GEtAllTypeGeomOFGeomColum("public")
        tabelasGeom = list(dataTables.keys())

        tabelasCamadas = []
        nomeFantasiaCamada =[]
        descricaoTabelasCamadas = []
        estiloCamadas = []
        aproximacao=[]

        if "TabelasDisponiveis" in config:
            tabelasGeom = config["TabelasDisponiveis"]

        if "TipoTabelasDisponiveis" in config:
            dataTables = dict(zip(tabelasGeom, config["TipoTabelasDisponiveis"]))

        if "tabelasCamadas" in config:
            tabelasCamadas = config["tabelasCamadas"]

        if "nomeFantasiaCamada" in config:
            nomeFantasiaCamada = config["nomeFantasiaCamada"]

        if "descricaoTabelasCamadas" in config:
            descricaoTabelasCamadas = config["descricaoTabelasCamadas"]

        if "estiloCamadas" in config:
            estiloCamadas = config["estiloCamadas"]
        if "aproximacao" in config:
            aproximacao = config["aproximacao"]

        self.objects_tables_disponiveis = tabelasGeom
        self.objects_tipo_tables_disponiveis = dataTables.values()
        nb_row = len(tabelasGeom)

        self.table_layers.setRowCount(nb_row)
        # itemCellClass = QTableWidgetItem(classe)

        for i in range(nb_row):
            index_checkUsar = -1
            if tabelasGeom[i] in tabelasCamadas:
                index_checkUsar = tabelasCamadas.index(tabelasGeom[i])
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

            defalt_proximidade = 0.00


            self.objects_file_style.append(self.create_filePath("filepath" + "-" + str(i) + "-" + str(5)))
            self.table_layers.setCellWidget(i, 5, self.objects_file_style[i])

            if tabelasGeom[i] in tabelasCamadas:
                itemidex = tabelasCamadas.index(tabelasGeom[i])
                #print("itemindex",itemidex)
                itemidex_aux = tabelasCamadas.index(tabelasGeom[i])
                if(len(estiloCamadas) !=0):
                    faixa_proximidade = aproximacao[itemidex]

                    defalt_proximidade = faixa_proximidade
                    print("faixa proximidade",faixa_proximidade)

                    self.objects_file_style[i].setFilePath(estiloCamadas[itemidex])

            self.objects_buffer.append(self.create_buffer_box("espessura" + "-" + str(i) + "-" + str(4), defalt_proximidade))
            self.table_layers.setCellWidget(i, 4, self.objects_buffer[i])

            self.objects_button_mais_infor.append(self.create_button_mais_inf("maisinfor" + "_" + str(i) + "_" + str(6) + "_" + str(index_checkUsar)))
            self.table_layers.setCellWidget(i, 6, self.objects_button_mais_infor[i])
            self.objects_button_mais_infor[i].clicked.connect(self.exec_more_infor)


    def save_base_pg(self):
        """
        Método responsável por Gravar as configurações das camadas de uma base de dados PostgreSQL
        @return: void
        """
        idbd = self.id_current_db
        config_db = self.setings02.get_config_database()
        config = {}
        for item in config_db:
            if item["id"] == idbd:
                config = item
        #print(type(config))

        config["TabelasDisponiveis"] = self.objects_tables_disponiveis
        config["TipoTabelasDisponiveis"] = list(self.objects_tipo_tables_disponiveis)
        #print("OIIIII", config["TipoTabelasDisponiveis"])
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
        #print("Aproximacao aqui: ",config["aproximacao"])

        aux = []

        for i in range(len(self.objects_tables_disponiveis)):
            if self.objects_vai_usar[i].checkState():
                aux.append(self.objects_nome_fantasia[i])

        config["nomeFantasiaCamada"] = aux

        if "maisInformacoesTabelas" not in config:
            aux = []
            for i in range(len(self.objects_tables_disponiveis)):
                aux.append({})
                config["maisInformacoesTabelas"] = aux

        aux = []
        for i in range(len(self.objects_tables_disponiveis)):
            if self.objects_vai_usar[i].checkState():
                aux.append(self.objects_file_style[i].filePath())

        config["estiloCamadas"] = aux

        #print(config)
        self.setings02.edit_database(self.id_current_db,config)

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

        if self.tipoFonte == "bd":
            self.save_base_pg()

        self.hide()
        self.continue_window.emit()

    def atualizar_obj_name(self):
        print ("tamanho obj infor:  ", len(self.objects_vai_usar ))
        for i in range(len(self.objects_vai_usar )):
            aux = self.objects_button_mais_infor[i].objectName()
            newName = aux.split("_")
            newName[3]=str(i)
            newName = "_".join(newName)
            self.objects_button_mais_infor[i].setObjectName(newName)

    def exec_more_infor(self):
        self.save_base_pg()
        self.atualizar_obj_name()

        btn = self.sender()

        print("MEU DEUS", btn.objectName())
        btn_name = btn.objectName()
        btn_name_array = btn_name.split("_")
        index_infor = btn_name_array[1]
        d = LayerInfor(self.id_current_db, int(index_infor))
        d.exec_()
        btn = self.sender()
        #print("MEU DEUS",jsonContest)




