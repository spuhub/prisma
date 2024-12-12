# SPU-PRISMA

O SPU-PRISMA, é um complemento (plugin) que adiciona funcionalidades ao software livre QGIS, com o objetivo de auxiliar a atividade de caracterização do patrimônio de imóveis da União (República Federativa do Brasil).

* *"Caracterização do Patrimônio": Conjunto de instrumentos técnicos administrativos de competência da SPU (Secretaria do Patrimônio da União) objetivando o levantamento das características espaciais, fisiográficas e ecológicas, considerando-se a dinâmica ambiental de forma integrada, de determinada área identificada como sendo da União, a partir dos aspectos definidos em lei.*

Em geral, essa ferramenta auxilia no estudo de sobreposição de um ou diversos imóveis (input), identificando sua interseção com áreas pertencentes à União ou com demais áreas temáticas (camadas) correlatas, identificando-o no espaço e proporcionando maior agilidade, bem como padronização, à geração dos documentos técnicos (Relatórios, Plantas e Memoriais Descritivos) pertinentes a essa atividade de gestão do patrimônio imobiliário da União.

Dado um polígono, linha, ponto ou endereço de entrada o complemento realiza a consulta de sobreposição nas fontes pré-cadastradas (Bancos de Dados Geográfico da SPU, WFS, *Shapefiles*), testando se as feições de entrada se sobrepõem ou não as demais fontes de dados escolhidas e levantando todas as suas características espaciais em relação aos imóveis da União. 

O SPU-PRISMA gera documentos em formato PDF com o resultado da caracterização. Tais documentos são compostos por mapas, tabela de coordenadas, informações sobre os imóveis que estão se sobrepondo entre outras informações sobre a sobreposição, como por exemplo a extensão da área sobreposta. 


## O que não é o SPU-PRISMA

* Um complemento para desenhar polígonos, pontos e linhas;

* Um complemento para atualização de geometria ou qualquer outra informação de bancos de dados geográficos ou de um conjunto de shapefile (SHP);

* Um complemento para fazer cadastro de imóveis;

* Um complemento para criar geometrias.


## Tipos de entradas de dados que o SPU-PRISMA aceita 

* Um endereço de um imóvel que será geocodificado e transformado em um ponto especializado;

* Uma feição selecionada de uma camada de projeto "em aberto" no QGIS, que pode ser de um dos tipos: Ponto, Linha ou Polígono;

* Um SHP com uma ou mais feições, que pode ser de um dos tipos: Ponto, Linha ou Polígono.


## Tipos bases de dados de comparação que o SPU-PRISMA consome

* Banco de dados Postgres/Postgis;

* Um diretório na máquina do usuário com Shapefiles;

* Um link WFS (*Web Feature Service*).

Essas bases foram concebidas para serem previamente especificadas por uma curadoria feita por técnicos da SPU e cadastradas no próprio complemento, dentro da janela de configurações.  

Ao cadastrar as bases no plugin será gerado um arquivo "JSON de curadoria", podendo o mesmo ser compartilhado entre os usuários da SPU, facilitando a disseminação das bases dados de consulta e promovendo uma uniformidade de fontes dados confiáveis.


## Manual do Usuário

Manual do usuário disponível [aqui](https://github.com/spuhub/prisma/tree/master/docs/manual_usuario).


## Download do SPU-PRISMA

[SPU-PRISMA na loja do QGIS](https://plugins.qgis.org/plugins/prisma/). 


## Equipe

### Gerente de Projeto: 
* Coordenação-Geral de Gestão de Base de Dados e Geoinformação (CGDAG-SPU)

### Líder de Projeto:
* Núcleo Regional de Geoinformação (NUGEO-SPU-SC)
* Jeuid Oliveira Junior (jeuid.junior@gestao.gov.br)

### Desenvolvedores:
* Vinicius Rafael Schneider (vinirafaelsch@gmail.com)
* Guilherme Henrique (guilherme.nascimento@gestao.gov.br)
