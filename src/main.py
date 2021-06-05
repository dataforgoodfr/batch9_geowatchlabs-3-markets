
import os 

#os.chdir('C:/Users/eurhope/Desktop/DFG/geowatchlab/3_prix_alim/batch9_geowatchlabs-3-markets/src')

from import_functions.get_agricultural_geo import *
from import_functions.clean_wilaya_moughataa import *

file_agg = './aggregated_match_for_FSMS_files_with_yields.csv'
file_agg = './aggregated_match_for_FSMS_files_with_yields_with_price_hl.csv'
file_agg = './standardized_aggregated_dataset.csv'

df_raw = pd.read_csv(file_agg)

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

income_col = df2.columns[df2.columns.str.contains('per.source')]
df2['income'] = df2[income_col].sum(axis=1)

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
