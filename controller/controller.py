import sys
import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

from ..screens.main_window import MainWindow
from ..settings.config_window import ConfigWindow
from ..screens.overlay_address import OverlayAddress
from ..screens.overlay_feature import OverlayFeature
from ..screens.overlay_shapefile import OverlayShapefile
from ..screens.select_databases import SelectDatabases

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
