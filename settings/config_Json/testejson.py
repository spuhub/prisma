# -*- coding: utf-8 -*-
import json



dados ={}
with open('dbtabases.json', 'r') as json_file:
    dados = json.load(json_file)
d= dados["base1"]


print(d)
print (type(d))
print(d["linhaferrea"])