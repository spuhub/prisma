import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
import shutil
from zipfile import ZipFile
import urllib3
import os
from PyQt5.QtWidgets import QMessageBox
import time

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dependency.ui'))


class Dependency(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super(Dependency, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        self.setupUi(self)
        self.button_install_dep.clicked.connect(self.install_dependecies)
        self.concluir.clicked.connect(self.concluir_process)



    def download(self):


        url = 'https://codeload.github.com/guilhermehrn/penv/zip/refs/heads/main'
        dir_path = os.path.dirname(os.path.realpath(__file__))
        nome = dir_path + "\penv.zip"
        http = urllib3.PoolManager()

        if os.path.isdir(os.path.join(dir_path, 'penv-main')):
            shutil.rmtree(os.path.join(dir_path, 'penv-main'))

        if os.path.isdir(os.path.join(dir_path, 'penv')):
            shutil.rmtree(os.path.join(dir_path, 'penv'))

        if os.path.isfile(os.path.join (dir_path, 'penv.zip')):
            shutil.rmtree(os.path.join (dir_path, 'penv-main'))

        with http.request('GET', url, preload_content=False) as r, open(nome, 'wb') as out_file:
            shutil.copyfileobj(r, out_file)

    def extract_files(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        nome = dir_path + "\penv.zip"
        z = ZipFile(nome, 'r')
        z.extractall(dir_path)
        z.close()

    def mover_file(self):

        dir_path = os.path.dirname(os.path.realpath(__file__))
        source_dir = dir_path + "\penv-main\penv\penv"
        destination_dir = dir_path + "\penv"
        shutil.move(source_dir, destination_dir)

    def delete_files(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.remove(dir_path + '\penv.zip')
        shutil.rmtree(dir_path + '\penv-main')


    def install_dependecies(self):
        self.button_install_dep.setEnabled(False)
        self.logText.setText("Fazendo download do arquivo zip.")
        self.progressBar.setEnabled(True)
        self.progressBar.setValue(2)
        self.download()
        self.logText.append("Download Concluído.")
        self.logText.append("Descompactando o arquivo Zip.")
        self.progressBar.setValue(40)
        self.extract_files()
        self.logText.append("Descompactação concluída.")
        self.logText.append("Movendo diretórios.")
        self.progressBar.setValue(65)
        self.mover_file()
        self.logText.append("Deletando arquivos desnecessário.")
        self.progressBar.setValue(80)
        self.delete_files()
        self.logText.append("Instalação concluída!")
        self.progressBar.setValue(100)

        self.concluir.setEnabled(True)

    def concluir_process(self):
        msg = QMessageBox(self)
        msg.information(self, "Dependências instaladas", "Para concluir a instalação é necessario fechar todas as janelas do Prisma e reiniciar o QGIS.")
        self.close()





