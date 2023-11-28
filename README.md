# mestrado-map-matching-for-smartdata

Programa de Map Matching para veículos autônomos. Como utilizar:

# Pastas 

## datasets

Contém um dataset de exemplo para utilização. 

## src

Essa pasta abriga os arquivos do programa, sendo eles:

### imuMock.py

Arquivo responsável por importar dados à partir da API do LISHA (Software/Hardware Integration Lab da UFSC), nele são feitas as requests para a API que contém os dados do dataset A2D2 (criado pela Audi):

https://lisha.ufsc.br/SDAV+-+A2D2+SmartData+Model

### app.py

Programa responsável por toda a lógica de map matching e identificação de centro de pista.

Duas maneira de utilização são demonstradas: 

1. Através de API de leitura de dados (simualação de leitura direta de sensor de GPS);
2. Através de importação de arquivo CSV disponibilizado na pasta datasets.

Nos dois casos, o programa vai lendo os dados e fazendo o map match em tempo de execução. No terminal é demonstrado o ponto de centro de pista (Latitude e Longitude)

### app_visual.py

Este programa é muito semelhante ao app.py, porém este também cria dois arquivos de mapa para demonstração dos traços e dos matches. Estes mapas são gerados nos arquivos trace_map.html e matches_map.html

# Execução

Instale os pacotes necessários:

    pip install -r requirements.txt


No arquivo app.py, é possível escolher a fonte de dados (API ou dataset csv). Isso fica na seção "Carregar dados da simulação". Para fins de teste, faça o uso do CSV "sample_trace_1.csv". Para tal, descomente a linha:
	
	complete_df = pd.read_csv("./datasets/sample_trace_1.csv")

Execute o arquivo src/app.py

    python src/app.py

Se tudo correr bem, o programa tentará gerar o centro de pista para cada leitura de GPS do CSV e em caso de encontrar a via, buscará a velocidade máxima permitida na pista. Abaixo exemplo de resultado:

	Leitura GPS: 39.679324, -104.934505
	Centro de Pista: 39.67835199999999, -104.933681
	Velocidade máxima: 65 mph