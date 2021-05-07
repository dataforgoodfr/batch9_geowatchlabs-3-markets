# -*- coding: utf-8 -*-

############################ Import libraries ############################

from Auxiliary_function_for_importing_data import *
import numpy as np

############################ First loop ############################

def initialize_relevant_labels(data_files_list, target_columns_cleaned, relevant_labels_clean):
    for data_file_index in range(len(data_files_list)):

        print(round(data_file_index/len(data_files_list)*100), " %")

        data_file_name = data_files_list[data_file_index]
        data, meta = get_data_with_filename(data_file_name)

        if not meta is None:
            column_names, label_names = meta.column_names, meta.column_labels

            column_names_clean = [clean(column_names[i]) for i in range(len(label_names)) if not label_names[i] is None and not column_names[i] is None]
            column_label_clean = [clean(label_names[i]) for i in range(len(label_names)) if not label_names[i] is None and not column_names[i] is None]

            perfect_match_indexes = [perfect_match_index(col, column_names_clean) for col in target_columns_cleaned]
            for id in perfect_match_indexes:
                if not id is None:
                    if column_names_clean[id] in relevant_labels_clean.keys():
                        relevant_labels_clean[column_names_clean[id]].append(column_label_clean[id])
                    else:
                        relevant_labels_clean[column_names_clean[id]] = [column_label_clean[id]]

############################ Second loop functions ############################

def count_column_names_loop(column_clean, all_column):
    for i in range(len(column_clean)):
        key = column_clean[i]
        if key in all_column.keys():
            all_column[key] += 1
        else:
            all_column[key] = 1

def get_best_match_with_column_name_loop(column_names_clean, target_columns_cleaned, data_file_name, best_match, equivalent_columns_table):
    best_candidate_by_name_row = []

    for col in target_columns_cleaned:
        to_test = list(set(equivalent_columns_table.loc[:, col])) + [col]
        column_min, distance_min = "", 100
        for col_test in to_test:
            id_name, distance_name = get_best_candidate_with_levenshtein_distance(col, column_names_clean)
            if distance_name < distance_min:
                distance_min = distance_name
                column_min = column_names_clean[id_name]
        best_candidate_by_name_row.append(column_min + "/" + str(distance_min))

    best_match.loc[data_file_name + "name"] = best_candidate_by_name_row + ["name"]

def get_best_match_with_column_label_loop(column_names_clean, target_columns_cleaned, data_file_name, best_match, relevant_labels_clean, column_label_clean):
    best_candidate_by_label_row = ["" for col in target_columns_cleaned]
    recorded_relevant_labels_clean = list(relevant_labels_clean.keys())

    for i in range(len(target_columns_cleaned)):
        col  = target_columns_cleaned[i]
        best_score = 100

        if col in relevant_labels_clean.keys():
            for col_label in relevant_labels_clean[col]:
                id_label, distance_label = get_best_candidate_with_levenshtein_distance(col_label, column_label_clean)
                if best_score > distance_label:
                    best_score, best_candidate_by_label_row[i] = distance_label, column_names_clean[id_label] + "/" + str(distance_label)

    best_match.loc[data_file_name + "label"] = best_candidate_by_label_row + ["label"]

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

relevant_labels_clean={}

### necessary to get better matches
### can be commented
initialize_relevant_labels(data_files_list, target_columns_cleaned, relevant_labels_clean)

all_column = {}
best_match = pd.DataFrame(data = [], columns=target_columns_cleaned + ['matching_type'])

print("------------- data processing --------------")

for data_file_index in range(len(data_files_list)):

    print(round(data_file_index/len(data_files_list)*100), " %")

    data_file_name = data_files_list[data_file_index]
    data, meta = get_data_with_filename(data_file_name)

    if not meta is None:
        nb_valid_files += 1

        column_names, label_names = meta.column_names, meta.column_labels

        column_names_clean = [clean(col) for col in column_names if not col is None]
        column_label_clean = [clean(col) for col in label_names if not col is None]
        column_clean = [clean(column_names[i]) + ";" + clean(label_names[i]) for i in range(len(label_names)) if not label_names[i] is None and not column_names[i] is None]

        ### You can comment if not necessary
        #count_column_names_loop(column_clean, all_column)
        get_best_match_with_column_name_loop(column_names_clean, target_columns_cleaned, data_file_name, best_match, equivalent_columns_table)
        #get_best_match_with_column_label_loop(column_names_clean, target_columns_cleaned, data_file_name, best_match, relevant_labels_clean, column_label_clean)

print("There are ",nb_valid_files ,"valid files")
print("There are ",len(data_files_list) - nb_valid_files," issues with files")

print("------------- exporting results -----------")

if not best_match.empty:
    best_match.to_csv("best_match_for_FSMS_files_columns.csv", sep=";")
