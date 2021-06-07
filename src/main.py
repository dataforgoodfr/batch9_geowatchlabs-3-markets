
import os 
import shutil
import numpy as np
import pandas as pd
from pathlib import Path
home = str(Path.home())

#os.chdir('C:/Users/eurhope/Desktop/DFG/geowatchlab/3_prix_alim/batch9_geowatchlabs-3-markets/src')

#
# MAKE DATA FROM RAW FILES
#

from import_functions.import_and_aggregate import *
# bug
data = import_dataset()
output_file = 'aggregated_match_for_FSMS_files_with_yields_with_price.csv'
shutil.copy(output_file, home + '/' + output_file)

from preprocessing.preprocessing import *

df_raw = preprocess_FSMS_files_with_yields_and_prices()

#
# IMPORT DATA
#

from import_functions.get_agricultural_geo import *
from import_functions.clean_wilaya_moughataa import *

file_agg = './aggregated_match_for_FSMS_files_with_yields.csv'
file_agg = './standardized_aggregated_dataset.csv'
file_agg = './aggregated_match_for_FSMS_files_with_yields_with_price.csv'

#df_raw = pd.read_csv(file_agg)

#
# CLEAN FROM MONTH
#

df = df_raw.dropna(subset={'month'})
df = df[df['month'].isin(['Decembre', 'Juin'])]

#
# CLEAN WILAYA AND MOUGHATAA NAMES
#

list_moughataa = df.moughataa.unique()
list_wilaya = df.wilaya.unique()

df2 = clean_moughataa_col(df)
df2 = clean_wilaya_col(df2)

list_moughataa2 = df2.moughataa.unique()
list_wilaya2 = df2.wilaya.unique()

#
# MAKE HOUSEHOLD GROUPS
#
col='revenu_mens'



test = pd.DataFrame(
            {
                "Mean": [np.mean(df2[col])],
                "Min": [np.min(df2[col])],
                "Q1": [np.quantile(df2[col], 0.25, axis=0)],
                "Median": [np.median(df2[col])],
                "Q3": [np.quantile(df2[col], 0.75, axis=0)],
                "Max": [np.max(df2[col])],
            })
    
                   
#income_col = df2.columns[df2.columns.str.contains('per.source')]
#df2['income'] = df2[income_col].sum(axis=1)





df2_11 = df2[df2['year'] == 2011]

df2_14dec = df2[(df2['year'] == 2014) & (df2['month'] == 'Decembre')]
df2_14dec['Tot_source'].unique()

df2_14jun = df2[(df2['year'] == 2014) & (df2['month'] == 'Juin')]
df2_14jun['Tot_source'].unique()

df2_15dec = df2[(df2['year'] == 2015) & (df2['month'] == 'Decembre')]
df2_15dec['Tot_source'].unique()

df2_15jun = df2[(df2['year'] == 2015) & (df2['month'] == 'Juin')]
df2_15jun['Tot_source'].unique()

df2_14dec['Tot_source'].mean()


inc = df2_14.income.unique()

import matplotlib.pyplot as plt

# An "interface" to matplotlib.axes.Axes.hist() method
n, bins, patches = plt.hist(data=df2_11, x='income',
                            bins='auto', color='#0504aa',
                            alpha=0.7, rwidth=0.85)

n, bins, patches = plt.hist(data=df2_14, x='income',
                            bins='auto', color='#0504aa',
                            alpha=0.7, rwidth=0.85)

# GET AGRICULTURAL MOUGHATAA

moughataa_agrc = get_agricultural_moughataa()
commune_agrc = get_agricultural_commune()
