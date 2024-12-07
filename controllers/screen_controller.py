from qgis.PyQt.QtWidgets import QMessageBox, QApplication

class Controller:
    """
    Classe que gerencia o controle das telas do sistema Prisma.

    Atributos:
        config_window (ConfigWindow): Classe responsável por manipular a tela de configuração.
        first_start (bool): Indica se a tela principal do Prisma já foi exibida.
        iface: Interface para acessar métodos do QGIS.
        main_window (MainWindow): Classe responsável por manipular a tela principal.
        overlay_feature_window (OverlayFeature): Classe responsável por manipular a tela de busca com feições selecionadas.
        overlay_point_window (OverlayPoint): Classe responsável por manipular a tela de busca por ponto.
        overlay_shapefile_window (OverlayShapefile): Classe responsável por manipular a tela de busca com shapefile como entrada.
        result_window (ResultWindow): Classe responsável por manipular a tela de resultados de sobreposição.
        select_databases (SelectDatabases): Classe responsável por manipular a tela de seleção de bases de dados para comparação.
        report_generator (ReportGenerator): Classe responsável por manipular a tela para preencher dados de cabeçalho e diretório de saída de relatórios PDF.
    """

    def __init__(self, iface):
        """
        Inicializa a classe Controller.

        Args:
            iface: Interface para acessar métodos do QGIS.
        """
        self.first_start = False
        self.iface = iface

    def show_main(self):
        """
        Exibe a tela principal do Prisma.
        Também funciona como controlador para transições entre telas.
        """
        from ..screens.main_window import MainWindow
        self.main_window = MainWindow(self.iface)
        self.main_window.switch_config.connect(self.show_config)
        self.main_window.switch_overlay_point.connect(self.show_overlay_point)
        self.main_window.switch_overlay_feature.connect(self.show_overlay_feature)
        self.main_window.switch_overlay_shapefile.connect(self.show_overlay_shapefile)
        self.main_window.switch_memorial_conversion.connect(self.show_memorial_conversion)

        self.main_window.show()

    def show_config(self):
        """
        Função acionada (e também serve como controller) para mostrar a tela de configuração do prisma.
        """
        msg = QMessageBox()
        msg.setWindowTitle("SPU-Prisma")
        msg.setText("Carregando configurações")
        msg.show()

        QApplication.processEvents()

        from ..settings.config_window import ConfigWindow
        self.config_window = ConfigWindow()
        self.config_window.back_window.connect(self.show_main)
        msg.close()
        self.config_window.show()

    def show_overlay_point(self):
        """
        Função acionada (e também serve como controller) para mostrar a tela de busca por ponto do prisma.
        """
        from ..screens.overlay_point import OverlayPoint
        self.overlay_point_window = OverlayPoint()
        self.overlay_point_window.back_window.connect(self.show_main)
        self.overlay_point_window.continue_window.connect(self.show_select_databases)
        self.overlay_point_window.show()

    def show_overlay_feature(self):
        """
        Função acionada (e também serve como controller) para mostrar a tela de busca através de feições selecionadas do prisma.
        """
        from ..screens.overlay_feature import OverlayFeature
        self.overlay_feature_window = OverlayFeature(self.iface)
        self.overlay_feature_window.back_window.connect(self.show_main)
        self.overlay_feature_window.continue_window.connect(self.show_select_databases)
        self.overlay_feature_window.show()

    def show_overlay_shapefile(self):
        """
        Função acionada (e também serve como controller) para mostrar a tela de busca através de input shapefile do prisma.
        """
        from ..screens.overlay_shapefile import OverlayShapefile
        self.overlay_shapefile_window = OverlayShapefile(self.iface)
        self.overlay_shapefile_window.back_window.connect(self.show_main)
        self.overlay_shapefile_window.continue_window.connect(self.show_select_databases)
        self.overlay_shapefile_window.show()

    def show_select_databases(self, operation_config):
        """
        Exibe a tela de seleção de bases de dados para comparação no Prisma.

        Args:
            operation_config (dict): Configurações da operação em andamento.
        """
        from ..screens.select_databases import SelectDatabases
        self.select_databases = SelectDatabases(operation_config)
        self.select_databases.cancel_window.connect(self.show_main)
        self.select_databases.continue_window.connect(self.show_result_window)
        self.select_databases.show()

    def show_report_generator(self, data):
        """
        Exibe a tela para inserção de dados de cabeçalho e diretório de saída dos relatórios PDF do Prisma.

        Args:
            data: Dados necessários para gerar o relatório.
        """
        from ..screens.report_generator import ReportGenerator
        self.report_generator = ReportGenerator(data)
        self.report_generator.show()

    def show_result_window(self, data):
        """
        Exibe a tela de resultados da análise de sobreposição no Prisma.

        Args:
            data: Dados gerados pela análise de sobreposição.
        """
        from ..screens.result_window import ResultWindow
        self.result_window = ResultWindow(data)
        self.result_window.report_generator_window.connect(self.show_report_generator)
        self.result_window.show()

    def show_memorial_conversion(self):
        """
        Função acionada (e também serve como controller) para mostrar a tela de busca através de input shapefile do prisma.
        """
        from ..screens.memorial_conversion import MemorialConversion
        self.overlay_shapefile_window = MemorialConversion(self.iface)
        self.overlay_shapefile_window.back_window.connect(self.show_main)
        self.overlay_shapefile_window.continue_window.connect(self.show_select_databases)
        self.overlay_shapefile_window.show()
