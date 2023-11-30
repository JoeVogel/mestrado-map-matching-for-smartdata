from pathlib import Path
import pandas as pd
import geopandas as gpd
import numpy as np
import osmnx as ox
import time
import webbrowser
import folium

from shapely.geometry import Point
from imuMock import ImuMock

from mappymatch import package_root
from mappymatch.constructs.geofence import Geofence
from mappymatch.constructs.trace import Trace
from mappymatch.maps.nx.nx_map import NxMap
from mappymatch.matchers.lcss.lcss import LCSSMatcher
from mappymatch.matchers.lcss.lcss import LCSSMatcher
from mappymatch.utils.crs import LATLON_CRS, XY_CRS
from mappymatch.utils.plot import plot_geofence, plot_matches, plot_trace


def match_to_road(m):
    d = {"road_id": m.road.road_id, "geom": m.road.geom}
    return d

def match_to_coord(m):
    d = {
        "road_id": m.road.road_id,
        "geom": Point(m.coordinate.x, m.coordinate.y),
        "distance": m.distance,
    }

    return d

def map_matcher(match_df):

    # É necessário criar um caminho com algumas coordenadas, para que o algoritmo consiga identificar o sentido do movimento na via
    trace = Trace.from_dataframe(match_df)

    # ---- Map Matching ------

    matcher = LCSSMatcher(nx_map)
    match_result = matcher.match_trace(trace)

    road_df = pd.DataFrame([match_to_road(m) for m in match_result.matches if m.road])

    if hasattr(road_df, 'road_id'):
        road_df = road_df.loc[road_df.road_id.shift() != road_df.road_id]
        
        road_gdf = gpd.GeoDataFrame(road_df, geometry=road_df.geom, crs=XY_CRS).drop(
            columns=["geom"]
        )
        road_gdf = road_gdf.to_crs(LATLON_CRS)

        coord_df = pd.DataFrame([match_to_coord(m) for m in match_result.matches if m.road])

        coord_gdf = gpd.GeoDataFrame(
            coord_df, geometry=coord_df.geom, crs=XY_CRS
        ).drop(columns=["geom"])
        coord_gdf = coord_gdf.to_crs(LATLON_CRS)

        mid_i = int(len(coord_gdf) / 2)
        mid_coord = coord_gdf.iloc[mid_i]
        
        return mid_coord
    else:
        return None

# ---- Carregar dados da simulação ------

# Ao usar no veículo, todo esse bloco deverá ser alterado para lidar com a busca dos dados de acordo com a aplicação
# a leitura do dado deverá ser feita dentro do loop

# Com mock IMU

# Gerar as coordenadas das medições do veículo

# imu_mock = ImuMock()

# data  = imu_mock.get_gps_iot_api(1533906414540000, 1600000000000000)

# complete_df = pd.DataFrame(data)

#Com CSV

# Gerar as coordenadas das medições do veículo
# complete_df = pd.read_csv("./datasets/resultado_INSS_ajustado_reduzido.csv")[:5000]
complete_df = pd.read_csv("./datasets/sample_trace_1.csv")

# ----- Termino carga dos dados -----

# ----- Processamento dos dados -----

data = {'latitude':[], 'longitude':[]}

# Inicia com dois elementos, pois o Trace precisa de pelo menos 2
data['latitude'].append(complete_df['latitude'][0])
data['latitude'].append(complete_df['latitude'][1])
data['longitude'].append(complete_df['longitude'][0])
data['longitude'].append(complete_df['longitude'][1])

df = pd.DataFrame.from_dict(data)

# Adição de ruído (opcional), de forma a verifiar se o map matching está funcionando
# df['latitude'] += np.random.normal(0, 0.0001, points.shape[0])
# df['longitude'] += np.random.normal(0, 0.0001, points.shape[0])

start_point = {'latitude': complete_df['latitude'].iloc[0], 'longitude': complete_df['longitude'].iloc[0]}
end_point = {'latitude': complete_df['latitude'].iloc[len(complete_df)-1], 'longitude': complete_df['longitude'].iloc[len(complete_df)-1]}

route_lst = []
route_lst.append(start_point)
route_lst.append(end_point)

route_df = pd.DataFrame(route_lst)

trace = Trace.from_dataframe(route_df)
geofence = Geofence.from_trace(trace, padding=1e4)
nx_map = NxMap.from_geofence(geofence)

tmap_file = Path("trace_map.html")
tmap = plot_trace(trace, plot_geofence(geofence))
tmap.save(str(tmap_file))
webbrowser.open(tmap_file.absolute().as_uri())

road_list = []

for u, v, d in nx_map.g.edges(data=True):
	if not isinstance(d['osmid'], list):
		if d not in road_list:
			road_list.append(d)

motion_vector_lst = []
last_road_id = ''
max_speed = None

start_time = time.time()

# Loop para simulação da execução ponto a ponto
j = 2
for j in range(len(complete_df)):
    
    point = map_matcher(df)

    if (point is not None):            
        print()
        
        print('Leitura GPS: {0}, {1}'.format(df['latitude'].iloc[len(df)-1], df['longitude'].iloc[len(df)-1]))
        
        print('Centro de Pista: {0}, {1}'.format(point.geometry.y, point.geometry.x))    

        if not point.road_id == last_road_id:
        
            # TODO: Implementar busca local da velocidade
            # road_data = list(filter(lambda element: element['osmid'] == 16986821, road_list))

            try:
                road_data = ox.features.features_from_point((point.geometry.y, point.geometry.x), tags={'maxspeed':True}, dist=50)
                max_speed = road_data['maxspeed'].iloc[0]
            except:
                print("Can't retrieve maxspeed")
            
            last_road_id = point.road_id
        
        print('Velocidade máxima: {0}'.format(max_speed))
        
        motion_vector = {'latitude':point.geometry.y, 'longitude':point.geometry.x, 'max_speed':max_speed}
        motion_vector_lst.append(motion_vector)
        
        print()

    if (len(df) >= 100):
        df = df.iloc[1:]

    new_location = {'latitude':[], 'longitude':[]}
    new_location['latitude'].append(complete_df['latitude'][j])
    new_location['longitude'].append(complete_df['longitude'][j])
    new_data_df = pd.DataFrame(new_location)

    df = pd.concat([df, new_data_df], ignore_index=True)
 
 
print("--- %s seconds ---" % (time.time() - start_time))

results_df = pd.DataFrame(motion_vector_lst)


print(results_df)




#  -------------------- Representação dos pontos no mapa -----------------------

plot = True

if plot:

    mid_i = int(len(results_df) / 2)
    mid_coord = results_df.iloc[mid_i]

    fmap = folium.Map(location=[mid_coord['latitude'], mid_coord['longitude']], zoom_start=11)

    for z in range(len(results_df)):
        folium.Circle(
                location=(results_df['latitude'].iloc[z], results_df['longitude'].iloc[z]),
                radius=5,
                tooltip=f"Max speed: {results_df['max_speed'].iloc[z]}"
            ).add_to(fmap)

    mmap_file = Path("map.html")
    mmap = fmap
    mmap.save(str(mmap_file))
    webbrowser.open(mmap_file.absolute().as_uri())