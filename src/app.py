from pathlib import Path
import pandas as pd
import geopandas as gpd
import numpy as np

from shapely.geometry import Point
from imuMock import ImuMock
from mappymatch import package_root
from mappymatch.constructs.geofence import Geofence
from mappymatch.constructs.trace import Trace
from mappymatch.maps.nx.nx_map import NxMap
from mappymatch.matchers.lcss.lcss import LCSSMatcher
from mappymatch.matchers.lcss.lcss import LCSSMatcher
from mappymatch.utils.crs import LATLON_CRS, XY_CRS


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
    # ---- Geração dos traços (caminhos) ------

    # print("loading trace.")

    trace = Trace.from_dataframe(match_df)

    # generate a geofence polygon that surrounds the trace; units are in meters;
    # this is used to query OSM for a small map that we can match to
    # print("building geofence.")
    geofence = Geofence.from_trace(trace, padding=1e3)

    # ---- Obter mapa do OSM ------

    # uses osmnx to pull a networkx map from the OSM database
    # print("pull osm map.")
    nx_map = NxMap.from_geofence(geofence)

    # ---- Map Matching ------

    # print("matching .")
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
        mid_coord = coord_gdf.iloc[mid_i].geometry
        
        return mid_coord.x, mid_coord.y
    else:
        return None, None

# ---- Carregar dados da simulação ------

# Ao usar no veículo, todo esse bloco deverá ser removido e 
# a leitura do dado deverá ser feita dentro do loop

# Com mock IMU

# Gerar as coordenadas das medições do veículo

# imu_mock = ImuMock()

# timestamp= 1533906414550000

# step = 10000
# data = {'latitude':[], 'longitude':[]}
# df = pd.DataFrame.from_dict(data)

# while True:

#     latitude, longitude = imu_mock.get_gps_iot_api(timestamp, timestamp + step)
    
#     print('{0}  |  {1}  |  {2}'.format(timestamp, latitude, longitude))
    
#     if (latitude != []):
        
#         if (len(df) > 10):
#             df = df.iloc[1:]
        
#         data = {'latitude':[], 'longitude':[]}
#         data['latitude'].append(latitude)
#         data['longitude'].append(longitude)
#         extended_df = pd.DataFrame(data)
        
#         df = pd.concat([df, extended_df], ignore_index=True)
        
#         route_center_latitude, route_center_longitude = map_matcher(df)  
    
#         if (latitude != None):
#             print('Centro de Pista: {0}, {1}'.format(route_center_latitude, route_center_longitude))
        
#         # Para evitar pegar o mesmo
#         timestamp = timestamp + step
        
#     timestamp = timestamp + step 


#Com CSV

# Gerar as coordenadas das medições do veículo
complete_df = pd.read_csv("./datasets/sample_trace_1.csv")

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

j = 2
for j in range(len(complete_df)):
    
    route_center_latitude, route_center_longitude = map_matcher(df)  
    
    if (route_center_latitude != None):
        print('Centro de Pista: {0}, {1}'.format(route_center_latitude, route_center_longitude))
    
    if (len(df) > 10):
        df = df.iloc[1:]
    
    data = {'latitude':[], 'longitude':[]}
    data['latitude'].append(complete_df['latitude'][j])
    data['longitude'].append(complete_df['longitude'][j])
    extended_df = pd.DataFrame(data)
    
    df = pd.concat([df, extended_df], ignore_index=True)
    