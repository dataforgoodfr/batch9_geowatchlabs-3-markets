# -*- coding: utf-8 -*-

from import_functions.import_and_aggregate import *
from import_functions.auxiliary_function_for_importing_data import extract_year_from_filename
import geopandas as gpd
import pandas as pd
import jellyfish

def get_mapping_commune():    
    
    file_commune = './Communes.geojson'    
    commune = gpd.read_file(file_commune)    
    commune = commune[['ADM3_REFNA', 'ID_3', 'geometry', 'ADM2_REFNA',  'ADM2_PCODE']]
    
    commune_moughataa = commune[['ADM2_REFNA']].drop_duplicates().reset_index()
    
    file_moughataa_new = './Moughataas_new.geojson'
    moughataa = gpd.read_file(file_moughataa_new)
    moughataa = moughataa[['X.1', 'ID_2', 'geometry']]
    
    list_commune_mg = []
    
    for m in range(len(commune_moughataa.index)):
        for k in range(len(moughataa.index)):
        
            match_name = commune_moughataa.loc[m, 'ADM2_REFNA']
            candidate = moughataa.loc[k,'X.1']        
            dist = jellyfish.levenshtein_distance(match_name, candidate)
            
            df = pd.DataFrame({'moughataa' : match_name, 
                               'candidate' : candidate,
                               'dist':dist}, index = [0])
            list_commune_mg.append(df)
            
    commune_mg = pd.concat(list_commune_mg)
    commune_mg = commune_mg[commune_mg['dist'] < 4].reset_index()
    #len(commune_mg2.index)
    
    # only match one moughata with candidate name
    commune_mg = commune_mg.sort_values("dist").groupby("candidate", as_index=False).first()
    commune_mg = commune_mg.rename(columns={'candidate':'X.1', 'moughataa':'ADM2_REFNA'})
    commune_mg = commune_mg.merge(moughataa, on= 'X.1', how='left')
    commune_mg = commune_mg[['X.1', 'ADM2_REFNA', 'ID_2']]
    #len(commune_mg3.index)
    
    commune_final = commune.merge(commune_mg, on = 'ADM2_REFNA', how = 'left')
    
    for i in range(len(commune_final)):   
        id2 = commune_final.loc[i,'ID_2']
        id3 = commune_final.loc[i,'ID_3']
        if (not pd.isna(id2)) & (not pd.isna(id3)):            
            commune_final.loc[i,'COMMUNE_ID'] = str(int(id2)) +  str(int(id3))
                                            
    commune_final = commune_final.rename(columns={'ADM3_REFNA': 'COMMUNE',
                                                  'ADM2_REFNA':'MOUGHATAA_1',
                                                  'X.1':'MOUGHATAA_2',
                                                  'ID_2':'MOUGHATAA_ID'})
    columns = pd.read_csv("./columns.csv")
    list_file = get_list_of_data_files('Mauritania FSMS data', 'sav')
    
    #order is not always sorted
    list_file.sort()

    for f in range(len(list_file)):
        
        data, meta =  pyreadstat.read_sav(list_file[f],
                                          apply_value_formats=True, encoding="ISO-8859-1")
        
        data = data[[columns.loc[f,'moughataa'], columns.loc[f,'commune']]]
        data = data.rename(columns={ columns.loc[f,'commune']:'COMMUNE_ID', columns.loc[f,'moughataa'] : 'MOUGHATAA'})
        data['COMMUNE_ID'] = [str(int(val)) for val in data['COMMUNE_ID']]
        
        data = data.merge(commune_final, on = 'COMMUNE_ID', how = 'left')
        
        moughC = commune_final[['MOUGHATAA_1', 'MOUGHATAA_2', 'MOUGHATAA_ID', 'ADM2_PCODE']].drop_duplicates()
        data_moughataa = data[['MOUGHATAA']].drop_duplicates()
        data_moughataa['MOUGHATAA_ID'] = data_moughataa['MOUGHATAA']
        data_moughataa = data_moughataa.merge(moughC, on = 'MOUGHATAA_ID', how = 'left')
    	
        break
    return(commune_final)