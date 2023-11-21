from pathlib import Path
import pandas as pd
import geopandas as gpd

from shapely.geometry import Point
from imuMock import ImuMock
from mappymatch import package_root
from mappymatch.constructs.geofence import Geofence
from mappymatch.constructs.trace import Trace
from mappymatch.maps.nx.nx_map import NxMap
from mappymatch.matchers.lcss.lcss import LCSSMatcher
from mappymatch.utils.crs import LATLON_CRS, XY_CRS

PLOT = True

if PLOT:
    import webbrowser

    from mappymatch.utils.plot import plot_geofence, plot_matches, plot_trace

# ---- Carregar dados da simulação ------

# Ao usar no veículo, todo esse bloco deverá ser removido e 
# a leitura do dado deverá ser feita dentro do loop

# Com mock IMU

# Gerar as coordenadas das medições do veículo

# imu_mock = ImuMock()

# timestamp= 1533906414550000

# i = 0
# step = 10000
# data = {'latitude':[], 'longitude':[]}

# # while True:
# while i < 5: # tem que ser maior do que 1 pois um traço precisa de dois pontos

#     latitude, longitude = imu_mock.get_gps_iot_api(timestamp, timestamp + step)
    
#     print('{0}  |  {1}  |  {2}'.format(timestamp, latitude, longitude))
    
#     if (latitude != []):
        
#         data["latitude"].append(latitude)
#         data["longitude"].append(longitude)
        
#         # Para evitar pegar o mesmo
#         timestamp = timestamp + step
#         i = i + 1
        
#     timestamp = timestamp + step 
    
# df = pd.DataFrame.from_dict(data)


#Com CSV

# Gerar as coordenadas das medições do veículo
df = pd.read_csv("./datasets/sample_trace_1.csv")


# ---- Geração dos traços (caminhos) ------

print("loading trace.")

trace = Trace.from_dataframe(df)

# generate a geofence polygon that surrounds the trace; units are in meters;
# this is used to query OSM for a small map that we can match to
print("building geofence.")
geofence = Geofence.from_trace(trace, padding=1e3)


# ---- Obter mapa do OSM ------

# uses osmnx to pull a networkx map from the OSM database
print("pull osm map.")
nx_map = NxMap.from_geofence(geofence)


# ---- Map Matching ------

print("matching .")
matcher = LCSSMatcher(nx_map)
match_result = matcher.match_trace(trace)

# ---- Visualização do traço e do resultado do Match (rua) ------

if PLOT:
    tmap_file = Path("trace_map.html")
    tmap = plot_trace(trace, plot_geofence(geofence))
    tmap.save(str(tmap_file))
    webbrowser.open(tmap_file.absolute().as_uri())

    mmap_file = Path("matches_map.html")
    mmap = plot_matches(match_result.matches)
    mmap.save(str(mmap_file))
    webbrowser.open(mmap_file.absolute().as_uri())