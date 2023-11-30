import pandas as pd

'''
Quando utilizamos um dataset com uma frequência de amostragem muito grande, precisamos reduzir o número de amostragens

Este programa recebe um dataset e o reduz de acordo com o fator de redução pretendido e cria um arquivo com o nome desejado na pasta datasets

Recomendado: o programa de Map Matching funciona bem com cerca de 1 leitura por segundo, portanto defina o fator de redução para obter essa quantidade

Ex.: datasets com leituras de 100Hz podem ser reduzidos com o fator de redução em 100

'''

reduction_factor = 100
new_file_name = "resultado_INSS_ajustado_reduzido"
use_complete_dataset = False
# Caso a flag acima seja definida como False, os valores abaixo precisarão ser preenchidos com as linhas de início e fim desejadas
start_line_load = 30000
final_line_load = 300000


# ----- Operation -----

complete_df = None

if use_complete_dataset:
	complete_df = pd.read_csv("./datasets/resultado_INSS_ajustado.csv")
else:
	complete_df = pd.read_csv("./datasets/resultado_INSS_ajustado.csv")[start_line_load:final_line_load]
	complete_df.index = range(len(complete_df))

complete_df = complete_df.round(decimals=6)
new_lst = []

# i = 0
# for index, row in complete_df.iterrows():
# 	if not(i % reduction_factor):
# 		new_lst.append(row)
# 	i = i + 1  

last_latitude = 0
last_langitude = 0

for index, row in complete_df.iterrows():
    
	latitude_diff = round((abs(row['latitude'] - last_latitude)), 6)
	longitude_diff = round((abs(row['longitude'] - last_langitude)), 6)

	if latitude_diff > 0.000001 or longitude_diff > 0.000001:
		new_lst.append(row)
  
		last_latitude = row['latitude']
		last_langitude = row['longitude']
  
complete_df = pd.DataFrame(new_lst) 
complete_df.index = range(len(new_lst)) 

complete_df.to_csv('./datasets/{0}.csv'.format(new_file_name))  