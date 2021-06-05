# -*- coding: utf-8 -*-

import pandas as pd
import jellyfish

def find_closest_string(list_string, list_candidate, no_perfect_match=True):
    list_df = []

    for k in range(len(list_string)):
        for c in range(len(list_candidate)):
            match_name = list_string[k]
            
            candidate = list_candidate[c]
            
            if not pd.isna(match_name):
                
                if not pd.isna(candidate):
                    
                    if no_perfect_match:
                        if candidate == match_name:
                            continue
                                        
                    dist = jellyfish.levenshtein_distance(match_name, candidate)
                    list_df.append(
                     pd.DataFrame({'string' : match_name, 
                                   'candidate' : candidate,
                                   'dist':dist}, index = [0]))              
            
    result = pd.concat(list_df)
    result = result.sort_values("dist").groupby("candidate", as_index=False).first()
    return(result)
    
def clean_moughataa_col(df):
    
    mg_list = find_closest_string(df.moughataa.unique(), df.moughataa.unique())
    mg_list = mg_list[mg_list['dist'] == 1].reset_index()
    
    for r in range(len(mg_list)):
        try:
            s = mg_list.loc[r, 'string']
            mg_list = mg_list[~(mg_list['candidate']==s)]
        except:
            pass
    #mg_list.loc[mg_list['candidate'] == 'teyarett', 'string'] = 'teyarett'
    
    try:
        mg_list = mg_list.reset_index(drop=False)
    except:
        pass
    
    mough = pd.DataFrame({'moughataa':df.moughataa.unique()})
    
    for s in range(len(mg_list.index)):
        string = mg_list.loc[s, 'string']
        string_replacing = mg_list.loc[s, 'candidate']
        mough.loc[mough['moughataa'] == string, 'moughataa2'] = string_replacing
    
    for m in range(len(mough.index)):
        if pd.isna(mough.loc[m, 'moughataa2']):
            mough.loc[m, 'moughataa2'] = mough.loc[m, 'moughataa']
            
            
    df = df.merge(mough, on = 'moughataa', how='left')
    df['moughataa'] = df['moughataa2']
    del df['moughataa2']
    
    #!!!! aoujeft n'existe pas comme moughataa dans trazdar
    #df.loc[df['moughataa'] == 'awjeft', 'moughataa'] = 'aoujeft'
    df.loc[df['moughataa'] == 'toujenine', 'moughataa'] = 'toujounine'
    #df.loc[df['moughataa'] == 'bouhdide', 'moughataa'] = 'boumdeid'
        
    return(df)
    
    
def clean_wilaya_col(df):
    try:
        df = df.reset_index(drop=False)
    except:
        pass
    
    list_wil = df.wilaya.unique()
    list_wil2 = []
    for i in range(len(list_wil)):
        if not pd.isna(list_wil[i]):
            wil = list_wil[i].upper().replace(' ', '_').replace('-', '_')
        else:
            wil = list_wil[i]
        list_wil2.append(wil)
        
    wil_match = find_closest_string(list_wil2, list_wil2)
    wil_match = wil_match.loc[(wil_match['dist'] == 1) | 
                              (wil_match['candidate'] == 'D_NOUADHIBOU')]
    
    for c in range(len(list_wil2)):
        wil = list_wil2[c]
        if wil in wil_match.candidate.unique():            
            wil2 = wil_match.loc[wil_match['candidate'] == wil, 'string']
            list_wil2[c] = list(wil2)[0]
    
    wil_df = pd.DataFrame({'wilaya':list_wil,
                          'wilaya2':list_wil2})
    
    df = df.merge(wil_df, on = 'wilaya', how='left')
    df['wilaya'] = df['wilaya2']
    del df['wilaya2']
    
    df.loc[df['wilaya'] == 'HODH_EL_GHARBI', 'wilaya'] = 'HODH_EL_GARBI'
    df.loc[df['wilaya'] == 'HODH_ECHARGUI', 'wilaya'] = 'HODH_ECHARGHI'
    
    return(df)

#
#    EXAMPLE
#    
 
#file_agg = './aggregated_match_for_FSMS_files_with_yields.csv'
#file_agg = './aggregated_match_for_FSMS_files_with_yields_with_price_hl.csv'
#file_agg = './standardized_aggregated_dataset.csv'

#df_raw = pd.read_csv(file_agg)

#df = df_raw.dropna(subset={'month'})

#list_moughataa = df.moughataa.unique()
#list_wilaya = df.wilaya.unique()

#df2 = clean_moughataa_col(df)
#df2 = clean_wilaya_col(df2)

#list_moughataa2 = df2.moughataa.unique()
#list_wilaya2 = df2.wilaya.unique()
