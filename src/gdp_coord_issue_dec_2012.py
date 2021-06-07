# -*- coding: utf-8 -*-

# !!!!!!!!!!!!!!!!!!!!!!!!!
#
# HOW TO GET LATITUDE AND LONGITUDE FROM GPS COORD ?
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

data['coord'] = data['GPScoord'].apply(clean_gps_coord)

# !!!!!!!!!!!!!!!!!!!!!!!!!
#
# HOW TO GET LATITUDE AND LONGITUDE FROM GPS COORD ?
#
# !!!!!!!!!!!!!!!!!!!!!

from auromat.coordinates.transform import ecef2Geodetic
ecef2Geodetic(-12.4381790776, 16.6586663039, 93.6809599455)

data.loc[0,'coord']
data.loc[0,'GPScoord']


from pykml import parser

root = parser.fromstring(data.loc[0,'GPScoord'])

# columns description