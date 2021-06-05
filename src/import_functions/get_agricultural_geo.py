# -*- coding: utf-8 -*-

import pandas as pd
import geopandas as gpd
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import descartes
import jellyfish
from shapely import geometry
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

def get_agricultural_moughataa():
    
    file_moughataa_new = './Moughataas_new.geojson'
    file_zone_me = "./Zones de moyen d'existence.geojson"
    
    moughataa = gpd.read_file(file_moughataa_new)
    zone_me = gpd.read_file(file_zone_me)
    
    area_culture_polygon = zone_me[zone_me['LZNUM'] == 9].geometry

    for i in range(len(moughataa.index)):
        moughataa_polygon = moughataa.loc[i, 'geometry']
        intersect = area_culture_polygon.intersection(moughataa_polygon)
        if intersect.is_empty.iloc[0]:
            moughataa.loc[i, 'in_culture_area'] = False
        else:
            moughataa.loc[i, 'in_culture_area'] = True
        
    moughataa_selected = moughataa[moughataa['in_culture_area'] == True]
    list_moughataa_selected = list(moughataa_selected['X.1'])
    
    return(list_moughataa_selected)
    
def get_agricultural_commune():
    
    file_commune = './Communes.geojson'
    file_zone_me = "./Zones de moyen d'existence.geojson"
    
    commune = gpd.read_file(file_commune)
    zone_me = gpd.read_file(file_zone_me)
    
    area_culture_polygon = zone_me[zone_me['LZNUM'] == 9].geometry

    for i in range(len(commune.index)):
        commune_polygon = commune.loc[i, 'geometry']
        intersect = area_culture_polygon.intersection(commune_polygon)    
        if intersect.is_empty.iloc[0]:
            commune.loc[i, 'in_culture_area'] = False
        else:
            commune.loc[i, 'in_culture_area'] = True
            
    commune_selected = commune[commune['in_culture_area'] == True]
    commune_selected = list(commune_selected['NAME_3'])
    return(commune_selected)

    