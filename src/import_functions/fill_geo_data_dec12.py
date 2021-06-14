# -*- coding: utf-8 -*-

from import_functions.auxiliary_function_for_importing_data import *
import pyreadstat
from math import sin, cos, sqrt, atan2, radians
import geopandas as gpd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

def distance(lat1, lon1, lat2, lon2):
    
    # approximate radius of earth in km
    R = 6373.0
    
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    
    return(distance)


def fill_geo_data_dec12(df):
    
    list_file = get_list_of_data_files('Mauritania FSMS data', 'sav')
    data, meta = pyreadstat.read_sav(list_file[5])
    
    dfdec12 = df[(df.year == 2012) & (df.month == 'Decembre')].reset_index(drop=True)
    dfdec12['GPScoord'] = data['GPScoord']
    
    def clean_gps_coord(string):
        string = string.replace('&lt;Point&gt;&lt;coordinates&gt;','')
        string = string.replace('&lt;/coordinates&gt;&lt;/Point&gt;','')
        return(string)
                
    def extract_lat_lon(string):    
        lon = string.split(',', 2)[0] 
        lat = string.split(',', 2)[1] 
        return lat, lon
                                
    dfdec12['coord'] = dfdec12['GPScoord'].apply(clean_gps_coord)
    
    file_moughataa_new = './Moughataas_new.geojson'
    moughataa = gpd.read_file(file_moughataa_new)
    moughataa = moughataa[['X.1', 'ID_2', 'geometry']].reset_index(drop=True)
    
    
    for i in range(len(dfdec12.index)):
        s = dfdec12.loc[i,'coord'] 
        lat, lon = extract_lat_lon(s)
        dfdec12.loc[i,'latitude'], dfdec12.loc[i,'longitude'] = lat, lon
        
        for m in range(len(moughataa.index)):
            poly = moughataa.loc[m, 'geometry']
        
        dfdec12.loc[i,'moughataa'] 
    
    
    
    
    
    # geodf = df[['wilaya', 'moughataa', 'latitude', 'longitude']]
    # geodf = geodf.drop_duplicates()
    # geodf = geodf.dropna()
    
    # geodf['latitude'] = round(geodf['latitude'],2)
    # geodf['longitude'] = round(geodf['longitude'],2)
    # geodf = geodf.drop_duplicates()
    
    # mough_geodf 
    
    # lat = []
    # long = []
    # for l in L :
    #   lat.append(l[0])
    #   long.append(l[1])

    # sum(lat)/len(lat)
    # sum(long)/len(long)
