import osmnx as ox
import pandas as pd
from skmob import TrajDataFrame
import networkx as nx
import folium
import time

# Obter dados do OpenStreetMap (mapa de interesse)
# north, south, east, west = -27.5954, -27.7266, -48.3920, -48.5805 # Região floripa

north, south, east, west = 39.7619, 39.5800, -104.6003, -105.1099
graph = ox.graph_from_bbox(north, south, east, west, network_type='all')


# Escolha os nós de origem e destino com base em suas coordenadas
#Floripa
# latitude_origem, longitude_origem = -27.6060, -48.4450  # Coordenadas de origem
# latitude_destino, longitude_destino = -27.6170, -48.4570  # Coordenadas de destino
#Exemplo
latitude_origem, longitude_origem = 39.65521, -104.919169  # Coordenadas de origem
latitude_destino, longitude_destino = 39.737989, -104.990321  # Coordenadas de destino

origem = ox.distance.nearest_nodes(graph, (latitude_origem, longitude_origem))
destino = ox.distance.nearest_nodes(graph, (latitude_destino, longitude_destino))

vehicle_data = []

# ---- Carregar dados da simulação ------

# Ao usar no veículo, todo esse bloco deverá ser removido e 
# a leitura do dado deverá ser feita dentro do loop

# Com mock IMU

# Gerar as coordenadas das medições do veículo
# traj_data = TrajDataFrame(vehicle_data, timestamp=True)

# imu_mock = ImuMock()

# for i in range(len(imu_mock.motion_vector_list)):
# 	latitude = imu_mock.motion_vector_list[i].pos["latitude"]
# 	longitude = imu_mock.motion_vector_list[i].pos["longitude"]
# 	timestamp = imu_mock.motion_vector_list[i].pos["timestamp"]
# 	vehicle_data.append((latitude, longitude, timestamp))


#Com CSV

# Gerar as coordenadas das medições do veículo
traj_data = TrajDataFrame(vehicle_data, timestamp=False)

df = pd.read_csv("./datasets/sample_trace_1.csv")

for index, row in df.iterrows():
    vehicle_data.append((row["latitude"], row["longitude"]))



# ----- Fim dados de simulação ----



# Loop para atualizar o trajeto à medida que o veículo se move
index = 0
while True:

	# ----- Processamento -----

	# Obtenha a última medição do GPS do veículo (substitua isso pelo código real de obtenção dos dados do GPS)
	# latitude, longitude, timestamp = 
	latitude = vehicle_data[index]["latitude"]
	longitude = vehicle_data[index]["longitude"]

	# Adicione a nova medição ao trajeto
	# traj_data = traj_data.append({'lat': latitude, 'lng': longitude, 'datetime': timestamp}, ignore_index=True)
	traj_data = traj_data.append({'lat': latitude, 'lng': longitude}, ignore_index=True)

	# Atualize o trajeto mapeado
	traj_data = traj_data.map_match(graph)

	# Encontre o novo caminho até o destino
	novo_caminho = nx.shortest_path(graph, source=traj_data.index[-2], target=destino, weight='length')

	#TODO: buscar a velocidade máxima da via


	# ----- Visualização (opcional)

	# Visualização do novo caminho no mapa
	m = folium.Map(location=[latitude_origem, longitude_origem], zoom_start=15)

	# Desenhe o trajeto mapeado no mapa
	for node in novo_caminho:
		node_data = graph.nodes[node]
		folium.CircleMarker(location=[node_data['y'], node_data['x']]).add_to(m)

	# Salve o mapa em um arquivo HTML (ou atualize a visualização em tempo real)
	m.save('map_matching_and_routing_result.html')

	# Aguarde um intervalo antes de obter a próxima medição do GPS
	# time.sleep(1)  # Exemplo: aguarde 1 segundo
	index += 1

