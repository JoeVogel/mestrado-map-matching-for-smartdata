from pathlib import Path
import pandas as pd
import numpy as np

from mappymatch import package_root
from mappymatch.constructs.geofence import Geofence
from mappymatch.constructs.trace import Trace
from mappymatch.maps.nx.nx_map import NxMap
from mappymatch.matchers.lcss.lcss import LCSSMatcher

PLOT = True

if PLOT:
    import webbrowser

    from mappymatch.utils.plot import plot_geofence, plot_matches, plot_trace


# ---- Carregar dados da simulação ------

vehicle_data = []

# Ao usar no veículo, todo esse bloco deverá ser removido e 
# a leitura do dado deverá ser feita dentro do loop

# Com mock IMU

# Gerar as coordenadas das medições do veículo

# imu_mock = ImuMock()

# data = {'latitude':[], 'longitude':[]}

# for i in range(len(imu_mock.motion_vector_list)):
# 	data[latitude].append(imu_mock.motion_vector_list[i].pos["latitude"])
# 	data[longitude].append(imu_mock.motion_vector_list[i].pos["longitude"])

# df = pd.DataFrame.from_dict(data)


#Com CSV

# Gerar as coordenadas das medições do veículo
df = pd.read_csv("./datasets/sample_trace_1.csv")


# ---- Geração dos traços (caminhos) ------

print("loading trace.")

# data = {'latitude':[39.655193, 39.655193], 'longitude':[-104.919294, -104.919294]}
# df = pd.DataFrame.from_dict(data)

# Adição de ruído (opcional), de forma a verifiar se o map matching está funcionando
df['latitude'] += np.random.normal(0, 0.0001, points.shape[0])
df['longitude'] += np.random.normal(0, 0.0001, points.shape[0])

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
