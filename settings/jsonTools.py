import json


class JsonTools:
    def __init__(self, jsonfile):
        self.jsonFile = jsonfile

    def GEtJson(self):

        with open(self.jsonFile, 'r') as json_file:
            dados = json.load(json_file)
        return dados


    def INsertDatabasePg(self, dbjsonconf):
        dados = {}

        with open(self.jsonFile, 'r') as json_file:
            dados = json.load(json_file)

        numofItens = len(list(dados.keys()))

        dbid = "base" + str(numofItens + 1)
        dbjsonconf ["id"] = dbid

        dados[dbid] = dbjsonconf
        with open(self.jsonFile, 'w') as json_file:
            json.dump(dados, json_file, indent=4)

        return dbid


    def EditDatabase(self, dbid, dbjsonnewconf):
        with open(self.jsonFile, 'r') as json_file:
            dados = json.load(json_file)

        dados[dbid] = dbjsonnewconf
        with open(self.jsonFile, 'w') as json_file:
            json.dump(dados, json_file, indent=4)




# d = JsonTools("./config_Json/dbtabases.json")
#
# p = d.GEtJson()
#
# db = p["base1"]
# d.INsertDatabasePg(db)
#
# print(type(p))


