
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
from import_functions.fill_geo_data_dec12 import *

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
# remove price columns
#
df = df.drop(columns={'price', 'category', 'cmid', 'ptid', 'umid',
                      'catid', 'sn', 'currency', 'unit', 'cmname',
                      'mktname', 'mktid'})
df = df.drop_duplicates()

# 
# FILL LATITUDE, LONGITUDE AND MOUGHATAA FOR DEC 2012
# 

df = fill_geo_data_dec12(df)

#
# CLEAN WILAYA AND MOUGHATAA NAMES
#

list_moughataa = df.moughataa.unique()
list_wilaya = df.wilaya.unique()

df2 = clean_moughataa_col(df)
df2 = clean_wilaya_col(df2)

list_moughataa2 = df2.moughataa.unique()
list_wilaya2 = df2.wilaya.unique()

df2_dec12 = df2[(df2.year == 2012) & (df2.month == 'Decembre')]

#
# MAKE HOUSEHOLD GROUPS
#

cols = df2.columns
revenu_col = list(cols[cols.str.contains('revenu|rev')])
col_interest = ['ident', 'year', 'month',
                'wilaya', 'moughataa', 'commune', 'milieu', 'latitude', 'longitude',
                'LHZ', 'fcs', 'csi', 
                'Nb_hom', 'Nb_fem','TxDep', 'Equiv_ad'] + revenu_col
                
col_crop = []

dftest= df2[df2['year'] == 2011][['year', 'month', 'rev_percap', 'revenu_mens', 'revenu1']] 

df2a = df2[col_interest]
df2a = df3.dropna(subset={'rev_percap'})

df2a = df2a[df2a['month'].isin(['Juin'])]

col = 'rev_percap'

list_year = [2012, 2013, 2014, 2015]
list_data_year = []

for y in list_year:
    
    df3 = df2a[df2a['year'] == y]    

    rev = pd.DataFrame(
                {
                    "Mean": [np.mean(df3[col])],
                    "Min": [np.min(df3[col])],
                    "Max": [np.max(df3[col])],
                    "Q1": [np.quantile(df3[col], 0.25, axis=0)],
                    "Q2": [np.quantile(df3[col], 0.5, axis=0)],               
                    "Q3": [np.quantile(df3[col], 0.75, axis=0)],               
                })        
        
    df3['rev_catg'] = np.select([(df3.rev_percap < rev.loc[0,'Q1']),
                                (df3.rev_percap >=  rev.loc[0,'Q1']) & (df3.rev_percap <  rev.loc[0,'Q2']),
                                 (df3.rev_percap >= rev.loc[0,'Q2']) & (df3.rev_percap <  rev.loc[0,'Q3']),
                                (df3.rev_percap >=  rev.loc[0,'Q3'])],
                                ["1", "2", "3", "4"])
    
    list_data_year.append(df3)

df3 = pd.concat(list_data_year)
df3['house_catg'] = df3['moughataa'] + df3['rev_catg']

data = df3.groupby(['house_catg', 'year'])['fcs', 'rev_percap'].mean().reset_index(drop=False)
  
datac = df3.value_counts(['house_catg', 'year']).reset_index(drop=False)
datac.columns = ['house_catg', 'year', 'n']

data = data.merge(datac, on = ['house_catg', 'year'], how = 'left')

#income_col = df2.columns[df2.columns.str.contains('per.source')]
#df2['income'] = df2[income_col].sum(axis=1)


#
# PANEL
#

from pandas.stats.plm import PanelOLS

data['year'] = pd.to_datetime(data['year'], format='%Y')

data = data.set_index('year', append=True)

model  = pd.stats.plm.PanelOLS(y=data['fsc'],x=data[['rev_percap']])

print model

from linearmodels import PanelOLS
mod = PanelOLS(data.fcs, data.rev_percap)
#entity_effects=True
pooled_res = mod.fit()
print(pooled_res)

# revenu absent en juin 2011??
# moughataa a determiner avec latitude longitude en dec 2012


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
