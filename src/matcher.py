import pandas as pd
import geopandas as gpd
import numpy as np
import osmnx as ox
import math

from shapely.geometry import Point

from mappymatch import package_root
from mappymatch.constructs.geofence import Geofence
from mappymatch.constructs.trace import Trace
from mappymatch.maps.nx.nx_map import NxMap
from mappymatch.matchers.lcss.lcss import LCSSMatcher
from mappymatch.utils.crs import LATLON_CRS, XY_CRS


class Matcher():
    
    def __init__(self) -> None:
        self.cache_df = pd.DataFrame({"latitude": [], "longitude": []})
        self.circular_polygn = None
        self.last_road_id = None
        self.max_speed = None
        
    
    def __create_circular_polygn(self, latitude, longitude, radius=5):
        # radius em km
        # Converte a coordenada para um objeto Point
        
        # Calcula os pontos do polígono circular
        polygn_points = {"latitude": [], "longitude": []}
        point_total = 50  # Ajuste conforme necessário
        
        for i in range(point_total):
            angle = math.radians(i * (360 / point_total))
             
            polygn_points['latitude'].append(latitude + (radius / 111) * math.sin(angle))
            polygn_points["longitude"].append(longitude + (radius / (111 * math.cos(math.radians(latitude)))) * math.cos(angle))
        
        df = pd.DataFrame(polygn_points)
         
        return df

    def __match_to_road(self, m):
        d = {"road_id": m.road.road_id, "geom": m.road.geom}
        return d

    def __match_to_coord(self, m):
        d = {
            "road_id": m.road.road_id,
            "geom": Point(m.coordinate.x, m.coordinate.y),
            "distance": m.distance,
        }

        return d
    
    def __add_new_location(self, latitude, longitude):
        new_location = {'latitude':[], 'longitude':[]}
        new_location['latitude'].append(latitude)
        new_location['longitude'].append(longitude)
        
        new_data_df = pd.DataFrame(new_location)

        self.cache_df = pd.concat([self.cache_df , new_data_df], ignore_index=True)
        
        del new_data_df
        del new_location
        
        # Tamanho do cache desejado
        if (len(self.cache_df) >= 300):
            self.cache_df = self.cache_df.iloc[1:]
    
    def create_map(self, start_point, end_point, print_map=False):
        
        route_lst = []
        route_lst.append(start_point)
        route_lst.append(end_point)

        route_df = pd.DataFrame(route_lst)
        
        trace = Trace.from_dataframe(route_df)
        geofence = Geofence.from_trace(trace, padding=1e4)
        self.nx_map = NxMap.from_geofence(geofence)
        
        if print_map:
            import webbrowser
            from pathlib import Path
            from mappymatch.utils.plot import plot_geofence, plot_trace
        
            tmap_file = Path("map.html")
            tmap = plot_trace(trace, plot_geofence(geofence))
            tmap.save(str(tmap_file))
            webbrowser.open(tmap_file.absolute().as_uri())
    
    def make_match(self, latitude, longitude):

        self.__add_new_location(latitude, longitude)
        
        # Só com uma coordenada não é possível realizar o map match
        if len(self.cache_df) > 1:
        
            # É necessário criar um caminho com algumas coordenadas, para que o algoritmo consiga identificar o sentido do movimento na via
            trace = Trace.from_dataframe(self.cache_df)

            # ---- Map Matching ------

            matcher = LCSSMatcher(self.nx_map)
            match_result = matcher.match_trace(trace)

            road_df = pd.DataFrame([self.__match_to_road(m) for m in match_result.matches if m.road])

            if hasattr(road_df, 'road_id'):
                road_df = road_df.loc[road_df.road_id.shift() != road_df.road_id]
                
                road_gdf = gpd.GeoDataFrame(road_df, geometry=road_df.geom, crs=XY_CRS).drop(
                    columns=["geom"]
                )
                road_gdf = road_gdf.to_crs(LATLON_CRS)

                coord_df = pd.DataFrame([self.__match_to_coord(m) for m in match_result.matches if m.road])

                coord_gdf = gpd.GeoDataFrame(
                    coord_df, geometry=coord_df.geom, crs=XY_CRS
                ).drop(columns=["geom"])
                coord_gdf = coord_gdf.to_crs(LATLON_CRS)

                mid_i = int(len(coord_gdf) / 2)
                mid_coord = coord_gdf.iloc[mid_i]
                
                if not self.last_road_id == mid_coord.road_id:
                    
                    try:
                        road_data = ox.features.features_from_point((mid_coord.geometry.y, mid_coord.geometry.x), tags={'maxspeed':True}, dist=50)
                        self.max_speed = road_data['maxspeed'].iloc[0]
                    except:
                        print("Can't retrieve maxspeed")
                
                self.last_road_id = mid_coord.road_id
                return {"latitude": mid_coord.geometry.y, "longitude":  mid_coord.geometry.x, "max_speed": self.max_speed}
            else:
                self.last_road_id = None
                self.max_speed = None
                
                return None
            
        else:
            return None
    