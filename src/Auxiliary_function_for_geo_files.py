# -*- coding: utf-8 -*-

import os, re
from pathlib import Path
import zipfile
import pandas as pd

def list_geo_file(folder=''):
   

    home = str(Path.home())

    zip_file = home + '/GeoWatch Labs Agricultural Maps.zip'
    root_folder = home + '/GeoWatch Labs Agricultural Maps/' + folder
    
    # unzip file
    if not os.path.exists(root_folder):
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(home)  
  
    # list all files in folder
    list_all_files = []
    for path, subdirs, files in os.walk(root_folder):
        for name in files:
            list_all_files.append(os.path.join(path, name))
    
    # list data files
    list_data_file = [f for f in list_all_files if re.search('.tif$', f)]
    
    return(list_data_file)
    
    
def df_geo_file():   
        
    def matching(string, pattern):
        for pat in pattern:
            if re.search(pat, string):
                return(pat)
                
    list_crop = ['cowpea', 'groundnut', 'maize', 'millet', 'sorghum']
    list_year = [str(n) for n in range(2010, 2015)]
    list_zone = ['zone1_' + str(i) for i in list(range(0, 14))][::-1]
    
    def class_year(string, pattern = list_year):
        return(matching(string, pattern))
        
    def class_zone(string, pattern = list_zone):
        return(matching(string, pattern))
    
    def class_crop(string, pattern = list_crop):
        return(matching(string, pattern))
        
    list_geomap = list_geo_file('Crop mapping')
    geomap_df = pd.DataFrame({'geomap_file' : list_geomap})
    geomap_df['zone'] = geomap_df['geomap_file'].apply(class_zone)
    
    list_yield_file = list_geo_file('Historical Yields')
    
    yield_df = pd.DataFrame({'yield_file' : list_yield_file})
    
    yield_df['year'] = yield_df['yield_file'].apply(class_year)
    yield_df['crop'] = yield_df['yield_file'].apply(class_crop)
    yield_df['zone'] = yield_df['yield_file'].apply(class_zone)
    
    files = yield_df.merge(geomap_df, on = 'zone', how='left')
    
    return(files)

def read_geo_file(file):
     
    from osgeo import gdal
    import matplotlib.pyplot as plt
    
    gdal_data = gdal.Open(file, gdal.GA_ReadOnly) 
    band = gdal_data.GetRasterBand(1)
    arr = band.ReadAsArray()
    plt.imshow(arr)    
    
#    dataset = gdal.Open(file)
#    data_array = gdal_data.ReadAsArray().astype(np.float)
#
#    prj = gdal_data.GetProjection()
#    print(prj)
   
    return(arr)