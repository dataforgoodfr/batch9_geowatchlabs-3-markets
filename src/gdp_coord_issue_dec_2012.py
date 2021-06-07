# -*- coding: utf-8 -*-

# !!!!!!!!!!!!!!!!!!!!!!!!!
#
# HOW TO GET LATITUDE AND LONGITUDE FROM GPS COORD ? 
# SOLUTION FOUND TO BE INCLUDED IN WORKFLOW (see below)
#
# !!!!!!!!!!!!!!!!!!!!!


import pandas as pd
import numpy as np
#%matplotlib inline
import matplotlib.pyplot as plt
import pyreadstat
import os, re
from pathlib import Path
import zipfile

def list_fsms_file():

    home = str(Path.home())

    zip_file = home + '/Mauritania FSMS data.zip'
    root_folder = home + '/Mauritania FSMS data'
    
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
    list_data_file = [f for f in list_all_files if re.search('.sav$', f)]
    
    return(list_data_file)
    
    
fsms_file = list_fsms_file()
        
data, meta =  pyreadstat.read_sav(fsms_file[5],
                                  apply_value_formats=True, encoding="ISO-8859-1")

def clean_gps_coord(string):
    string = string.replace('&lt;Point&gt;&lt;coordinates&gt;','')
    string = string.replace('&lt;/coordinates&gt;&lt;/Point&gt;','')
    return(string)

def extract_latitude(string):    
     lon = string.split(',', 2)[0] 
     lat = string.split(',', 2)[1] 
     return lat, lon


data['coord'] = data['GPScoord'].apply(clean_gps_coord)

for i in range(len(data.index)):
    s = data.loc[i,'coord'] 
    data.loc[i,'Latitude'],  data.loc[i,'Longitude'] = extract_latitude(s)
