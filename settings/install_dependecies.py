"""
    funções para instalar dependencias no sistema antes de iniciar o plugin
"""
import os
import subprocess

arq_dependencias = os.path.join(os.path.dirname(__file__), 'dependencies')
flag_dependencias = os.path.join(os.path.dirname(__file__), 'flag_dependencies')

def recupera_instalacao_qgis():
    """
        Busca nos diretórios existentes uma instalação do qgis
        returns list[paths]
    """
    lista_bat = []

    paths = [r"C:\\", r"D:\\", r"E:\\"]
    for directory in paths:
        if os.path.exists(directory):
            for root, dirs, files in os.walk(directory):
                if "QGIS" in root:
                    for file in files:
                        if file == "python-qgis-ltr.bat" or file == "python-qgis.bat":
                            caminho = os.path.join(root, file)
                            print(caminho)
                            lista_bat.append(f'"{caminho}"')
                            break

    return lista_bat


def instala_dependencias(dependencias):
    """
        realiza instalação das dependencias em todas os python encontrados
        returns None
    """
    lista_bat = recupera_instalacao_qgis()
    lista_dependencias = []
    # lista = [r'"c://python.bat"']
    with open(dependencias, 'r', encoding='utf-8') as arquivo:
        for dependencia in arquivo:
            lista_dependencias.append(dependencia)

    for python in lista_bat:
        for dependencia in lista_dependencias:
            comando = ' '.join((python, dependencia))

            process = subprocess.Popen(comando)
            process.wait()
            process.kill()


def verifica_flag_dependencias(flag_dependencias):
    """
        realiza checagem de flag de instalação das dependencias em todas os python encontrados
        returns Str
    """
    with open(flag_dependencias, 'r', encoding='utf-8') as arquivo:
        for line in arquivo:
            return line