import os
import json

class JsonTools:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.json_path = base_dir + "\settings\dbtabases.json"
        with open(self.json_path, 'r', encoding='utf8') as f:
            self.json_config = json.load(f)


    def InsertDatabasePg(self, dbjsonconf):
        dados = {}

        with open(self.json_path, 'r') as f:
            dados = json.load(f)

        numofItens = len(list(dados.keys()))

        dbid = "base" + str(numofItens + 1)
        dbjsonconf ["id"] = dbid

        dados[dbid] = dbjsonconf
        with open(self.json_path, 'w') as f:
            json.dump(dados, f, indent=4)

        return dbid


    def EditDatabase(self, dbid, dbjsonnewconf):
        with open(self.json_path, 'r') as f:
            dados = json.load(f)

        dados[dbid] = dbjsonnewconf
        with open(self.json_path, 'w') as f:
            json.dump(dados, f, indent=4)

    def GetConfigShapefile(self):
        shp_list = []

        for base, data in self.json_config.items():
            if(data['tipo'] == 'shp'):
                shp_list.append(data)

        return shp_list

    def GetConfigDatabase(self):
        shp_list = []

        for base, data in self.json_config.items():
            if(data['tipo'] == 'pg'):
                shp_list.append(data)

        return shp_list

if __name__ == '__main__':
    d = JsonTools()

    saida = d.GetConfigDatabase()
    d.InsertDatabasePg(saida[0])
    print(d.GetConfigDatabase())





