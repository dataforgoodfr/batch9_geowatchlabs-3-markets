# -*- coding: utf-8 -*-

############################ Import libraries ############################

import zipfile
import pandas as pd
import numpy as np
import re
import pyreadstat
import os
import os.path
from pathlib import Path
import errno
import jellyfish

############################ Auxiliary functions ############################

def unzip_data():
    current_directory = str(Path().absolute())

    correct_zip_file = [f for f in os.listdir(current_directory) if f[:20] == "Mauritania FSMS data"]
    if len(correct_zip_file) == 0:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), "Mauritania FSMS data")

    zip_file = os.path.join(current_directory, correct_zip_file[-1])
    root_folder = os.path.join(current_directory, "Mauritania FSMS data%%%%.zip")

    # unzip file
    if not os.path.exists(root_folder):
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(current_directory)

def get_list_of_data_files():
    current_directory = str(Path().absolute())

    root_folder = os.path.join(current_directory, 'Mauritania FSMS data')

    # list all files in folder
    list_all_files = []
    for path, subdirs, files in os.walk(root_folder):
        for name in files:
            list_all_files.append(os.path.join(path, name))

    # list data files
    list_data_file = [f for f in list_all_files if re.search('.sav$', f)]

    return list_data_file

def get_data_with_filename(file):
    try:
        # read data
        data, meta =  pyreadstat.read_sav(file, apply_value_formats=True, encoding="ISO-8859-1")
        return data, meta
    except:
        print("Need to investigate ",file)
        return None, None

def clean(name):
    #seperate in words
    name_lowercase = name.lower()
    relevant_words = re.findall(r'[a-z]+', name_lowercase)

    #remove one letter words
    relevant_words = [word for word in relevant_words if len(word) > 1]

    relevant_sentence = " ".join(relevant_words)
    return relevant_sentence

def get_best_candidate_with_levenshtein_distance(match_name, candidates_name):
    distance_by_candidate = [jellyfish.levenshtein_distance(match_name, candidate) for candidate in candidates_name]
    distance_min = min(distance_by_candidate)

    return distance_by_candidate.index(distance_min), distance_min

def perfect_match_index(match_name, candidates_name):
    try:
        return candidates_name.index(match_name)
    except:
        return None

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

def get_best_match_with_column_name_loop(column_names_clean, target_columns_cleaned, data_file_name, best_match):
    best_candidate_by_name_row = []

    for col in target_columns_cleaned:
        id_name, distance_name = get_best_candidate_with_levenshtein_distance(col, column_names_clean)
        best_candidate_by_name_row.append(column_names_clean[id_name] + "/" + str(distance_name))

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

def aggregate_matching_column_loop(data, column_names_clean, data_file_name, target_columns_cleaned,column_names):
    perfect_match_indexes = [perfect_match_index(col, column_names_clean) for col in target_columns_cleaned]
    perfect_match_columns = [column_names[id] for id in perfect_match_indexes if not id is None]
    temp = data[perfect_match_columns]
    temp.columns = [column_names_clean[id] for id in perfect_match_indexes if not id is None]
    return temp

def aggregate_matching_column_moments_loop(data, column_names_clean, data_file_name, column_names):
    perfect_match_indexes = [perfect_match_index(col, column_names_clean) for col in target_columns_cleaned]
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

target_columns = ['NUMQUEST', 'IDENT', 'ENQU', 'Hors_NK', 'MOUGHATAA', 'COMMUNE',
              'VILLAG0', 'VILLAGE', 'MILIEU', 'NUMEN', 'DATE',
              'CDATSAISIE', 'CODE_ENQ', 'CODE_CONT', 'FCS', 'CSI']
target_columns_cleaned = [clean(col) for col in target_columns if not col is None]

relevant_labels_clean={}

### necessary to get better matches
### can be commented
initialize_relevant_labels(data_files_list, target_columns_cleaned, relevant_labels_clean)

all_column = {}
best_match = pd.DataFrame(data = [], columns=target_columns_cleaned + ['matching_type'])
match = pd.DataFrame(data = [], columns=target_columns_cleaned)
match_moments = pd.DataFrame(data = [], columns=["variable", "Path", "Mean", "Min", "Q1", "Median" "Q3", "Max"])

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
        count_column_names_loop(column_clean, all_column)
        get_best_match_with_column_name_loop(column_names_clean, target_columns_cleaned, data_file_name, best_match)
        get_best_match_with_column_label_loop(column_names_clean, target_columns_cleaned, data_file_name, best_match, relevant_labels_clean, column_label_clean)
        match = match.append(aggregate_matching_column_loop(data, column_names_clean, data_file_name, target_columns_cleaned,column_names))
        match_moments = match_moments.append(aggregate_matching_column_moments_loop(data, column_names_clean, data_file_name, column_names))

print("There are ",nb_valid_files ,"valid files")
print("There are ",len(data_files_list) - nb_valid_files," issues with files")

print("------------- exporting results -----------")

if all_column:
    df = pd.DataFrame.from_dict(all_column, orient='index')
    df = df.reset_index().rename(columns={0 : 'Nb', 'index': 'key'})
    df[['Name','Label']] = df.key.str.split(";",expand=True,)
    df = df.drop(["key"], axis=1)
    df.to_csv("all_column_in_FSMS_files.csv", sep=";")

if not best_match.empty:
    best_match.to_csv("best_match_for_FSMS_files_columns.csv", sep=";")

if not match.empty:
    match.reset_index()
    match.to_csv("aggregated_match_for_FSMS_files.csv", sep=";")

if not match_moments.empty:
    match_moments.reset_index()
    match_moments.to_csv("aggregated_match_moments_for_FSMS_files.csv", sep=";")
