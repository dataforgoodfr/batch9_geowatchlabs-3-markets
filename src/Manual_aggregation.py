# -*- coding: utf-8 -*-

############################ Import libraries ############################

from Auxiliary_function_for_importing_data import *
import numpy as np
import math

############################ loop functions ############################

def aggregate_matching_column_loop(data, column_names_clean, data_file_name, eq_target_columns_cleaned, column_names):
    perfect_match_indexes = [perfect_match_index(col, column_names_clean) for col in eq_target_columns_cleaned if not col is None]
    perfect_match_columns = [column_names[id] for id in perfect_match_indexes if not id is None]
    temp = data[perfect_match_columns]
    temp.columns = [col for col in eq_target_columns_cleaned if not col is None and not perfect_match_index(col, column_names_clean) is None]
    temp['Path'] = data_file_name
    return temp

def aggregate_matching_column_moments_loop(data, column_names_clean, data_file_name, column_names, eq_target_columns_cleaned):
    perfect_match_indexes = [perfect_match_index(col, column_names_clean) for col in eq_target_columns_cleaned if col != ""]
    perfect_match_columns =  [column_names[id] for id in perfect_match_indexes if not id is None]
    temp = pd.DataFrame(data = [], columns=["variable", "Path", "Mean", "Min", "Q1", "Median" "Q3", "Max"])
    for col in perfect_match_columns:
        if data[col].dtypes.kind in "fi":
            temp = temp.append(pd.DataFrame({"variable" : [col], "Path" : [data_file_name], "Mean" : [np.mean(data[col])],
                    "Min" : [np.min(data[col])], "Q1" : [np.quantile(data[col], 0.25, axis=0)], "Median": [np.median(data[col])],
                    "Q3" : [np.quantile(data[col], 0.75, axis=0)], "Max" : [np.max(data[col])]}))
    return temp

############################ code ############################

unzip_data()

print("------------- data unzipped ---------------")

data_files_list = get_list_of_data_files()
nb_valid_files = 0

print("------------- initializing ----------------")

equivalent_columns_table = pd.read_csv("columns.csv", sep=";", header = 0)
equivalent_columns_table.columns = [clean(col) for col in equivalent_columns_table.columns]

target_columns = ['NUMQUEST', 'IDENT', 'ENQU', 'Hors_NK', 'MOUGHATAA', 'COMMUNE',
                'VILLAG0', 'VILLAGE', 'MILIEU', 'WILAYA', 'LATITUDE', 'LONGITUDE',
                'ALTITUDE', 'NUMEN', 'DATE', 'CDATSAISIE', 'CODE_ENQ', 'CODE_CONT',
                'LHG', 'LHZ', 'FCS', 'CSI']
target_columns_cleaned = [clean(col) for col in target_columns if not col is None]

### can be commented
match = pd.DataFrame(data = [], columns=target_columns_cleaned)
match_moments = pd.DataFrame(data = [], columns=["variable", "Path", "Mean", "Min", "Q1", "Median" "Q3", "Max"])

print("------------- data processing --------------")

for data_file_index in range(len(data_files_list)):

    print(round(data_file_index/len(data_files_list)*100), " %")

    data_file_name = data_files_list[data_file_index]
    data, meta = get_data_with_filename(data_file_name)

    if not meta is None:
        nb_valid_files += 1

        column_names_clean = [clean(col) for col in meta.column_names if not col is None]
        eq_target_columns = [clean(equivalent_columns_table.loc[data_file_index, col]) for col in target_columns_cleaned]

        ### removing duplicates
        eq_target_columns_cleaned = list(set(eq_target_columns))

        ### You can comment if not necessary
        match = match.append(aggregate_matching_column_loop(data, column_names_clean, data_file_name, eq_target_columns_cleaned, meta.column_names))
        match_moments = match_moments.append(aggregate_matching_column_moments_loop(data, column_names_clean, data_file_name, meta.column_names, eq_target_columns_cleaned))

### add year and month data

match['year'] = match['Path'].apply(extract_year_from_filename)
match['month'] = match['Path'].apply(extract_month_from_filename)


print("There are ",nb_valid_files ,"valid files")
print("There are ",len(data_files_list) - nb_valid_files," issues with files")

print("------------- exporting results -----------")

if not match.empty:
    match.reset_index()
    match.to_csv("aggregated_match_for_FSMS_files.csv", sep=";", index = False)

if not match_moments.empty:
    match_moments.reset_index()
    match_moments.to_csv("aggregated_match_moments_for_FSMS_files.csv", sep=";", index = False)
