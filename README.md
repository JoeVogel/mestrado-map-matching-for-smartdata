# mestrado-map-matching-for-smartdata

Programa de Map Matching para veículos autônomos. Como utilizar:

# Pastas 

## datasets

Contém um dataset de exemplo para utilização. 

## src

Essa pasta abriga os arquivos do programa, sendo eles:

### imuMock.py

Arquivo responsável por importar dados à partir da API do LISHA (Software/Hardware Integration Lab da UFSC), nele são feitas as requests para a API que contém os dados do dataset OpenCood:

https://lisha.ufsc.br/SDAV+-+A2D2+SmartData+Model

### matcher.py

Classe responsável por toda a lógica de map matching e identificação de centro de pista.

Principais métodos:

```
def create_map(self, start_point, end_point, print_map=False)
```

Este método faz a criação de um mapa local contendo o grafo das estradas para utilização posterior

* start_point: é o ponto inicial do trajeto
* end_point: é o ponto final do trajeto
* print_map: caso True, ele irá gerar um arquivo HTML para representação visual do polígono utilizado para carga do grafo

start_point e end_point são coordenadas geográficas utilizadas para a limitação do mapa a ser carregado em memória. Isso pode ser obtido através do gerenciador de viagem ou colocado arbitráriamente 

```
def make_match(self, latitude, longitude)
```

Este método é chamado para fazer o map matching, para que o match aconteça, faz-se necessário que o cache (self.cache_df) tenha alguns registros, portanto, as primeiras execuções retornarão None, porém após algumas leituras o mpetodo retornará um Motion Vector contendo as coordendas do centro de pista e a velocidade máxima para a rua 

A implementação utiliza uma versão alterada do seguinte repositório:

https://github.com/NREL/mappymatch

Este programa implementa o map-matching baseado no método proposto em:

	Zhu, Lei, Jacob R. Holden, and Jeffrey D. Gonder.
    "Trajectory Segmentation Map-Matching Approach for Large-Scale, High-Resolution GPS Data."
    Transportation Research Record: Journal of the Transportation Research Board 2645 (2017): 67-75.

## example

Essa pasta abriga um exemplo de utilização do programa:

### demonstration.py

Programa para demonstração de utilização do Map Matcher. Este programa pode ser executado importando dados da API do Lisha ou via carga de Dataset

Neste arquivo, note o uso do Matcher() através dos métodos: create_map() e make_match(). O primeiro cria um grafo de uma área pré-determinada, enquanto o segundo faz o Map Matching para cada leitura do GPS

# Execução

Instale os pacotes necessários:

    pip install -r requirements.txt


Execute o arquivo example/demonstration.py

```
python example/demonstration.py
```

Se tudo correr bem, o programa tentará gerar o centro de pista para cada leitura de GPS e em caso de encontrar a via, buscará a velocidade máxima permitida na pista. Abaixo exemplo de resultado:

```
{'latitude': 39.719714999999994, 'longitude': -104.958337, 'max_speed': '30 mph'}
```