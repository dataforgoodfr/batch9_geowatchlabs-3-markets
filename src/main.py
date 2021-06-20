
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

dftest= df2[df2['year'] == 2012][['year', 'month', 'rev_percap', 'revenu_mens', 'revenu1']] 

df2a = df2[col_interest]
df2a = df2a.dropna(subset={'rev_percap'})

#df2a = df2a[df2a['month'].isin(['Juin'])]

col = 'rev_percap'

list_year = [2012, 2013, 2014, 2015]
list_month = ['Decembre', 'Juin']
list_data_year = []

for y in list_year:
    for m in list_month:
    
        df3 = df2a[(df2a['year'] == y) & (df2a['month'] == m)]    
    
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

data = df3.groupby(['house_catg', 'year', 'month', 'moughataa', 'rev_catg'])['fcs', 'rev_percap'].mean().reset_index(drop=False)
  
datac = df3.value_counts(['house_catg', 'year', 'month']).reset_index(drop=False)
datac.columns = ['house_catg', 'year', 'month', 'n']

data = data.merge(datac, on = ['house_catg', 'year', 'month'], how = 'left')

#
# CREATE TIME COLUMN
# 

time_df = data[['year', 'month']].drop_duplicates()
time_df = time_df.sort_values('month', ascending=False).sort_values('year')
time_df = time_df.reset_index(drop=True).reset_index(drop=False)
time_df.columns = ['time', 'year', 'month']

data = data.merge(time_df, on = ['year', 'month'], how = 'left')
data = data.sort_values('time').reset_index(drop=True)

data = data.set_index(['house_catg', 'time'])

data['month_Decembre'] = pd.get_dummies(data)['month_Decembre']

data['rev_percap'] = data['rev_percap']/1000

#income_col = df2.columns[df2.columns.str.contains('per.source')]
#df2['income'] = df2[income_col].sum(axis=1)


#
# PANEL
#
from linearmodels import BetweenOLS

w = data.n
mod = BetweenOLS.from_formula('fcs ~ rev_percap + month_Decembre + EntityEffects',
                            data = data, weights=w)
mod.fit()

# INTERPRETATION : TO BE FULLY CHECKED
# une augmentation de 1000 du revenu par rapport à sa moyenne sur a période
# augmente de X le score fcs par rapport à sa moyenne sur a période

#
# ESTIMATION EXCLUDING DECEMBER
#

datajun = data[data['month'].isin(['Juin'])].reset_index(drop=False)
datajun = datajun.drop(columns={'time'})
time_df = datajun[['year', 'month']].drop_duplicates()
time_df = time_df.sort_values('month', ascending=False).sort_values('year')
time_df = time_df.reset_index(drop=True).reset_index(drop=False)
time_df.columns = ['time', 'year', 'month']

datajun = datajun.merge(time_df, on = ['year', 'month'], how = 'left')
datajun = datajun.sort_values('time').reset_index(drop=True)
datajun = datajun.set_index(['house_catg', 'time'])

w = datajun.n
mod = BetweenOLS.from_formula('fcs ~ rev_percap + EntityEffects',
                            data = datajun, weights=w)
mod.fit()