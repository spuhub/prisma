class Controller:
    """
    Classe que faz o controle das telas.

    @ivar config_window: Armazena a classe que manipula a tela de configuração.
    @ivar first_start: Após aparecer a primeira tela do Prisma, variável passa a ser True sempre. Serve para fazer o controle de telas.
    @ivar iface: Variável para acessar métodos do QGIS.
    @ivar main_window: Armazena a classe que manipula a tela principal.
    @ivar overlay_feature_window: Armazena a classe que manipula a tela para busca com feições selecionadas.
    @ivar overlay_point_window: Armazena a classe que manipula a tela para busca através de pontos.
    @ivar overlay_shapefile_window: Armazena a classe que manipula a tela para busca com shapefile de input.
    @ivar result_window: Armazena a classe que manipula a tela de resultados de sobreposição.
    @ivar select_databases: Armazena a classe que manipula a tela de seleção de bases de dados para comparação.
    @ivar 	report_generator: Armazena a classe que manipula a tela para preencher dados de cabeçalho e diretório de saída dos relatórios PDF.
    """

    def __init__(self, iface):
        """
        Método de inicialização da classe.
        """
        self.first_start = False
        self.iface = iface

    def show_main(self):
        """
        Função acionada (e também serve como controller) para mostrar a tela principal do prisma.
        """
        from ..screens.main_window import MainWindow
        self.main_window = MainWindow(self.iface)
        self.main_window.switch_config.connect(self.show_config)
        self.main_window.switch_overlay_point.connect(self.show_overlay_point)
        self.main_window.switch_overlay_feature.connect(self.show_overlay_feature)
        self.main_window.switch_overlay_shapefile.connect(self.show_overlay_shapefile)

        self.main_window.show()

    def show_config(self):
        """
        Função acionada (e também serve como controller) para mostrar a tela de configuração do prisma.
        """
        from ..settings.config_window import ConfigWindow
        self.config_window = ConfigWindow()
        self.config_window.back_window.connect(self.show_main)
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
        Função acionada (e também serve como controller) para mostrar a tela de seleção de bases de dados para comparação do prisma.
        """
        from ..screens.select_databases import SelectDatabases
        self.select_databases = SelectDatabases(operation_config)
        self.select_databases.cancel_window.connect(self.show_main)
        self.select_databases.continue_window.connect(self.show_result_window)
        self.select_databases.show()

    def show_report_generator(self, data):
        """
        Função acionada (e também serve como controller) para mostrar a tela onde o usuário insere os dados de cabeçalho e local onde devem ser gerados os relatórios PDF do prisma.
        """
        from ..screens.report_generator import ReportGenerator
        self.report_generator = ReportGenerator(data)
        self.report_generator.show()

    def show_result_window(self, data):
        """
        Função acionada (e também serve como controller) para mostrar a tela de resultados do prisma.
        """
        from ..screens.result_window import ResultWindow
        self.result_window = ResultWindow(data)
        self.result_window.report_generator_window.connect(self.show_report_generator)
        self.result_window.show()
