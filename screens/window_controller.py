import sys
import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi
from ..settings.config_window import ConfigWindow

class MainWindow (QtWidgets.QDialog):

    switch_config = QtCore.pyqtSignal()
    switch_overlay_address = QtCore.pyqtSignal()
    switch_overlay_feature = QtCore.pyqtSignal()
    switch_overlay_shapefile = QtCore.pyqtSignal()

    def __init__(self):

        super(MainWindow, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'main_window.ui'), self)

        self.btn_config.clicked.connect(self.go_to_config)
        self.btn_endereco.clicked.connect(self.go_to_address)
        self.btn_feicao.clicked.connect(self.go_to_feature)
        self.btn_shapefile.clicked.connect(self.go_to_shapefile)

    def go_to_config(self):
        self.switch_config.emit()

    def go_to_address(self):
        self.switch_overlay_address.emit()

    def go_to_feature(self):
        self.switch_overlay_feature.emit()

    def go_to_shapefile(self):
        self.switch_overlay_shapefile.emit()



class OverlayAddress (QtWidgets.QDialog):

    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self):
        super(OverlayAddress, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'overlay_address.ui'), self)

        self.btn_voltar.clicked.connect(self.back)
        self.btn_continuar.clicked.connect(self.next)

    def back(self):
        self.hide()
        self.back_window.emit()

    def next(self):
        self.hide()
        self.continue_window.emit()

class OverlayFeature (QtWidgets.QDialog):

    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self):
        super(OverlayFeature, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'overlay_feature.ui'), self)

        self.btn_voltar.clicked.connect(self.back)
        self.btn_continuar.clicked.connect(self.next)

    def back(self):
        self.hide()
        self.back_window.emit()

    def next(self):
        self.hide()
        self.continue_window.emit()

class OverlayShapefile (QtWidgets.QDialog):
    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self):
        super(OverlayShapefile, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'overlay_shapefile.ui'), self)

        self.btn_voltar.clicked.connect(self.back)
        self.btn_continuar.clicked.connect(self.next)

    def back(self):
        self.hide()
        self.back_window.emit()

    def next(self):
        self.hide()
        self.continue_window.emit()

class SelectDatabases(QtWidgets.QDialog):
    continue_window = QtCore.pyqtSignal()

    def __init__(self):
        super(SelectDatabases, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'select_databases.ui'), self)

        self.btn_continuar.clicked.connect(self.next)

    def next(self):
        self.hide()
        self.continue_window.emit()

class Controller:

    def __init__(self, iface):
        self.first_start = False
        self.iface = iface

    def show_main(self):
        self.main_window = MainWindow()
        self.main_window.switch_config.connect(self.show_config)
        self.main_window.switch_overlay_address.connect(self.show_overlay_address)
        self.main_window.switch_overlay_feature.connect(self.show_overlay_feature)
        self.main_window.switch_overlay_shapefile.connect(self.show_overlay_shapefile)

        if not self.first_start:
            self.first_start = True
            self.main_window.show()

    def show_config(self):
        self.config_window = ConfigWindow()
        self.config_window.back_window.connect(self.show_main)
        self.config_window.show()

    def show_overlay_address(self):
        self.overlay_address_window = OverlayAddress()
        self.overlay_address_window.back_window.connect(self.show_main)
        self.overlay_address_window.continue_window.connect(self.show_select_databases)
        self.overlay_address_window.show()

    def show_overlay_feature(self):
        self.overlay_feature_window = OverlayFeature()
        self.overlay_feature_window.back_window.connect(self.show_main)
        self.overlay_feature_window.continue_window.connect(self.show_select_databases)
        self.overlay_feature_window.show()

    def show_overlay_shapefile(self):
        self.overlay_shapefile_window = OverlayShapefile()
        self.overlay_shapefile_window.back_window.connect(self.show_main)
        self.overlay_shapefile_window.continue_window.connect(self.show_select_databases)
        self.overlay_shapefile_window.show()

    def show_select_databases(self):
        self.select_databases = SelectDatabases()
        self.select_databases.show()

# Função só é executada fora do plugin, utilizada para testes durante o desenvolvimento
def main():
    app = QtWidgets.QApplication(sys.argv)
    controller = Controller()
    controller.show_main()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()