from pathlib import Path
import pandas as pd
import geopandas as gpd
import sys

sys.path.insert(0, './src/')

from lisha_opencood import LishaOpenCood
from matcher import Matcher

# ---- Carregar dados da simulação ------

# Com API LISHA

# Gerar as coordenadas das medições do veículo

# lisha_api = LishaOpenCood()

# data  = imu_mock.get_gps_iot_api()

# complete_df = pd.DataFrame(data)


#Com CSV

# Gerar as coordenadas das medições do veículo
complete_df = pd.read_csv("./datasets/sample_trace_1.csv")

# ----- Termino carga dos dados -----

matcher = Matcher()

start_point = {'latitude': complete_df['latitude'].iloc[0], 'longitude': complete_df['longitude'].iloc[0]}
end_point = {'latitude': complete_df['latitude'].iloc[len(complete_df)-1], 'longitude': complete_df['longitude'].iloc[len(complete_df)-1]}

matcher.create_map(start_point, end_point, False)

motion_vector_lst = []

# Loop para simulação da execução ponto a ponto
j = 2
for j in range(len(complete_df)):
    
    current_latitude = complete_df['latitude'].iloc[j]
    current_longitude = complete_df['longitude'].iloc[j]
    
    match_result = matcher.make_match(current_latitude, current_longitude)
 
    print(match_result)
    motion_vector_lst.append(match_result)
 

results_df = pd.DataFrame(motion_vector_lst)


print(results_df)




#  -------------------- Representação dos pontos no mapa -----------------------

# plot = True

# if plot:

#     mid_i = int(len(results_df) / 2)
#     mid_coord = results_df.iloc[mid_i]

#     fmap = folium.Map(location=[mid_coord['latitude'], mid_coord['longitude']], zoom_start=11)

#     for z in range(len(results_df)):
#         folium.Circle(
#                 location=(results_df['latitude'].iloc[z], results_df['longitude'].iloc[z]),
#                 radius=5,
#                 tooltip=f"Max speed: {results_df['max_speed'].iloc[z]}"
#             ).add_to(fmap)

#     mmap_file = Path("map_matches.html")
#     mmap = fmap
#     mmap.save(str(mmap_file))
#     webbrowser.open(mmap_file.absolute().as_uri())