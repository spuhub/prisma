import os.path

from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

#from .config_layers import ConfigLayers
#from .json_tools import JsonTools
#from .env_tools import EnvTools
from PyQt5.QtWidgets import QMessageBox

from ..screens.report_generator import ReportGenerator
from ..databases.db_connection import DbConnection


class LayerInfor(QtWidgets.QDialog):
    """Classe reponsavel por manipular a janela de configuração principal"""

    back_window = QtCore.pyqtSignal()
    continue_window = QtCore.pyqtSignal()

    def __init__(self):
        super(LayerInfor, self).__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'layer_infor.ui'), self)
