# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

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


    list_col_income = []
    
    # decembre 2014
    f=9
    data, meta =  pyreadstat.read_sav(fsms_file[f],
                                      apply_value_formats=True, encoding="ISO-8859-1")
    col = data.columns
    col_income = col.str.contains('rev|source')
    revenu14dec = data[col[col_income]]
    list_col_income.append(list(col[col_income]))
    
    #juin 2014
    f = 10
    data, meta =  pyreadstat.read_sav(fsms_file[f],
                                      apply_value_formats=True, encoding="ISO-8859-1")
    col = data.columns
    col_income = col.str.contains('rev|source')
    revenu14jun = data[col[col_income]]
    list_col_income.append(list(col[col_income]))
   
    #juin 2013
    f = 8
    data, meta =  pyreadstat.read_sav(fsms_file[f],
                                      apply_value_formats=True, encoding="ISO-8859-1")
    col = data.columns
    col_income = col.str.contains('rev|source')
    revenu13jun = data[col[col_income]]
    list_col_income.append(list(col[col_income]))
    
    #dec 2013
    f = 7
    data, meta =  pyreadstat.read_sav(fsms_file[f],
                                      apply_value_formats=True, encoding="ISO-8859-1")
    col = data.columns
    col_income = col.str.contains('rev|source')
    revenu13dec = data[col[col_income]]
    list_col_income.append(list(col[col_income]))
    
    #juin 2012
    f = 6
    data, meta =  pyreadstat.read_sav(fsms_file[f],
                                      apply_value_formats=True, encoding="ISO-8859-1")
    col = data.columns
    col_income = col.str.contains('rev|source')
    revenu12jun = data[col[col_income]]
    list_col_income.append(list(col[col_income]))
    
    # dec 2012
    f = 5
    data, meta =  pyreadstat.read_sav(fsms_file[f],
                                      apply_value_formats=True, encoding="ISO-8859-1")
    col = data.columns
    col_income = col.str.contains('rev|source')
    revenu12dec = data[col[col_income]]
    list_col_income.append(list(col[col_income]))
    
    # dec 2015
    f = 11
    data, meta =  pyreadstat.read_sav(fsms_file[f],
                                      apply_value_formats=True, encoding="ISO-8859-1")
    col = data.columns
    col_income = col.str.contains('rev|source')
    revenu15dec = data[col[col_income]]
    list_col_income.append(list(col[col_income]))
    
    # dec 2015
    f = 12
    data, meta =  pyreadstat.read_sav(fsms_file[f],
                                      apply_value_formats=True, encoding="ISO-8859-1")
    col = data.columns
    col_income = col.str.contains('rev|source')
    revenu15jun = data[col[col_income]]
    list_col_income.append(list(col[col_income]))
    
    # jun 2011
    f = 3
    data, meta =  pyreadstat.read_sav(fsms_file[f],
                                      apply_value_formats=True, encoding="ISO-8859-1")
    col = data.columns
    col_income = col.str.contains('rev|source')
    revenu11jun = data[col[col_income]]
    list_col_income.append(list(col[col_income]))
    
    # dec 2011
    f = 0
    data, meta =  pyreadstat.read_sav(fsms_file[f],
                                      apply_value_formats=True, encoding="ISO-8859-1")
    col = data.columns
    col_income = col.str.contains('rev|source')
    revenu11dec = data[col[col_income]]
    list_col_income.append(list(col[col_income]))
    
    