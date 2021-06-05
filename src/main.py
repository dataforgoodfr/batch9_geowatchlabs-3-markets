
import os 

#os.chdir('C:/Users/eurhope/Desktop/DFG/geowatchlab/3_prix_alim/batch9_geowatchlabs-3-markets/src')

from import_functions.get_agricultural_geo import *
from import_functions.clean_wilaya_moughataa import *

file_agg = './aggregated_match_for_FSMS_files_with_yields.csv'
file_agg = './aggregated_match_for_FSMS_files_with_yields_with_price_hl.csv'
file_agg = './standardized_aggregated_dataset.csv'

df_raw = pd.read_csv(file_agg)

df = df_raw.dropna(subset={'month'})

list_moughataa = df.moughataa.unique()
list_wilaya = df.wilaya.unique()

#
# CLEAN WILAYA AND MOUGHATAA NAMES
#

df2 = clean_moughataa_col(df)
df2 = clean_wilaya_col(df2)

list_moughataa2 = df2.moughataa.unique()
list_wilaya2 = df2.wilaya.unique()

# GET AGRICULTURAL MOUGHATAA

moughataa_agrc = get_agricultural_moughataa()
commune_agrc = get_agricultural_commune()
