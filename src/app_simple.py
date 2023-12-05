from pathlib import Path
import pandas as pd
import geopandas as gpd
import numpy as np
import osmnx as ox
import time
import requests
import json

def match_service_request(points):
    
    coordinates = ''
    radiuses = ''
    
    for i in range (len(points)):
        
        if i == 0:
            coordinates = coordinates + str(points[i][0]) + ',' + str(points[i][1])
            radiuses = radiuses + '49'
        else:
            coordinates = coordinates + ';' + str(points[i][0]) + ',' + str(points[i][1])
            radiuses = radiuses + ';' + '49'
    
    url = "http://router.project-osrm.org/match/v1/driving/{0}?overview=full&radiuses={1}".format(coordinates, radiuses)
    params = {
        "steps": "true",
        "geometries": "geojson",
        "overview": "full",
    }

    data = {"coordinates": points}

    # response = requests.post(url, params=params, json=data)
    response = requests.post(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro na solicitação: {response.status_code}")
        return None

# complete_df = pd.read_csv("./datasets/sample_trace_1.csv")
complete_df = pd.read_csv("./datasets/resultado_INSS_ajustado_reduzido.csv")[30000:31000]
complete_df.index = range(len(complete_df))

points = []

points.append([complete_df['longitude'][0], complete_df['latitude'][0]])
points.append([complete_df['longitude'][0], complete_df['latitude'][0]])

motion_vector_lst = []
max_speed = None


# Loop para simulação da execução ponto a ponto
j = 2
for j in range(len(complete_df)):
    
    point = match_service_request(points)

    if (point is not None):            
        print()
        
        print('Leitura GPS: {0}, {1}'.format(complete_df['latitude'].iloc[j], complete_df['longitude'].iloc[j]))
        
        latitude_waypoint = point["tracepoints"][len(point["tracepoints"]) - 1]["location"][1]
        longitude_waypoint = point["tracepoints"][len(point["tracepoints"]) - 1]["location"][0]
        
        print('Centro de Pista: {0}, {1}'.format(latitude_waypoint, longitude_waypoint))    

        try:
            road_data = ox.features.features_from_point((latitude_waypoint, longitude_waypoint), tags={'maxspeed':True}, dist=50)
            max_speed = road_data['maxspeed'].iloc[0]
        except:
            max_speed = None
            print("Can't retrieve maxspeed")
        
        print('Velocidade máxima: {0}'.format(max_speed))
        
        motion_vector = {'latitude':latitude_waypoint, 'longitude':longitude_waypoint, 'max_speed':max_speed}
        motion_vector_lst.append(motion_vector)
        
        print()

    if (len(points) >= 2):
        points.pop(0)

    points.append([complete_df['longitude'][j], complete_df['latitude'][j]])
 


results_df = pd.DataFrame(motion_vector_lst)


print(results_df)

