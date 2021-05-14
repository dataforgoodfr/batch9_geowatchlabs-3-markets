# -*- coding: utf-8 -*-

############################ Import libraries ############################

from Auxiliary_function_for_importing_data import *
import numpy as np
import math

############################ loop functions ############################

def aggregate_matching_column_loop(data, column_names, data_file_name, eq_target_column, target_columns):
    perfect_match_indexes = [perfect_match_index(col, column_names) for col in eq_target_column if not col is None]
    perfect_match_columns = [column_names[id] for id in perfect_match_indexes if not id is None]
    temp = data[perfect_match_columns]
    temp.columns = [target_columns[i] for i in range(len(eq_target_column)) if not eq_target_column[i]  is None and not perfect_match_index(eq_target_column[i] , column_names) is None]
    return temp

def aggregate_matching_column_moments_loop(data, column_names, data_file_name, eq_target_column, target_columns):
    perfect_match_indexes = [perfect_match_index(col, column_names) for col in eq_target_column if col != ""]
    temp = pd.DataFrame(data = [], columns=["variable", "Path", "Mean", "Min", "Q1", "Median" "Q3", "Max"])
    for i in range(len(perfect_match_indexes)):
        id = perfect_match_indexes[i]
        if not id is None:
            col = column_names[id]
            if data[col].dtypes.kind in "fi":
                temp = temp.append(pd.DataFrame({"variable" : [target_columns[i]], "Path" : [data_file_name], "Mean" : [np.mean(data[col])],
                        "Min" : [np.min(data[col])], "Q1" : [np.quantile(data[col], 0.25, axis=0)], "Median": [np.median(data[col])],
                        "Q3" : [np.quantile(data[col], 0.75, axis=0)], "Max" : [np.max(data[col])]}))
    return temp

############################ code ############################

unzip_data("Mauritania FSMS data")

print("------------- data unzipped ---------------")

data_files_list = get_list_of_data_files("Mauritania FSMS data", ".sav")
nb_valid_files = 0

print("------------- initializing ----------------")

equivalent_columns_table = pd.read_csv("columns.csv", sep=",", header = 0)

target_columns = [col for col in equivalent_columns_table.columns if str(col) != "nan"]

### can be commented
match = pd.DataFrame(data = [], columns=target_columns)
match_moments = pd.DataFrame(data = [], columns=["variable", "Path", "Mean", "Min", "Q1", "Median" "Q3", "Max"])

print("------------- data processing --------------")

for data_file_index in range(len(data_files_list)):

    print(round(data_file_index/len(data_files_list)*100), " %")

    data_file_name = data_files_list[data_file_index]
    data, meta = get_data_with_filename(data_file_name)

    if not meta is None:
        nb_valid_files += 1

        column_names = [col for col in meta.column_names if not col is None]
        eq_target_columns = [equivalent_columns_table.loc[data_file_index, col] for col in target_columns]

        ### You can comment if not necessary
        match = match.append(aggregate_matching_column_loop(data, column_names, data_file_name, eq_target_columns, target_columns))
        match_moments = match_moments.append(aggregate_matching_column_moments_loop(data, column_names, data_file_name, eq_target_columns, target_columns))

print("There are ",nb_valid_files ,"valid files")
print("There are ",len(data_files_list) - nb_valid_files," issues with files")

print("------------- exporting results -----------")

match['year'] = match['Path'].apply(extract_year_from_filename)
match['month'] = match['Path'].apply(extract_month_from_filename)

if not match.empty:
    match.reset_index()
    match.to_csv("aggregated_match_for_FSMS_files.csv", sep=",", index = False)

if not match_moments.empty:
    match_moments.reset_index()
    match_moments.to_csv("aggregated_match_moments_for_FSMS_files.csv", sep=",", index = False)
