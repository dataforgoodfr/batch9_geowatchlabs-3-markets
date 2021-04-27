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

    root_folder = current_directory + '/Mauritania FSMS data'

    # list all files in folder
    list_all_files = []
    for path, subdirs, files in os.walk(root_folder):
        for name in files:
            list_all_files.append(os.path.join(path, name))

    # list data files
    list_data_file = [f for f in list_all_files if re.search('.sav$', f)]

    return list_data_file

def convert_data(file):
    try:
        # read data
        data, meta =  pyreadstat.read_sav(file, apply_value_formats=True)
        return data, meta
    except:
        print("Need to investigate ",file)
        return None, None

def clean_name(name):
    #seperate in words
    name_lowercase = name.lower()
    relevant_words = re.findall(r'[a-z]+', name_lowercase)

    #remove one letter words
    relevant_words = [word for word in relevant_words if len(word) > 1]

    relevant_sentence = " ".join(relevant_words)
    return relevant_sentence

def get_best_candidate_with_levenshtein_distance(match_name, candidates_name):
    distance_by_candidate_name = [jellyfish.levenshtein_distance(match_name, candidate) for candidate in candidates_name]
    distance_min_name = min(distance_by_candidate_name)

    return candidates_name[distance_by_candidate_name.index(distance_min_name)] + "/" + str(distance_min_name)

def perfect_match_index(match_name, candidates_name):
    try:
        return candidates_name.index(match_name)
    except:
        return None

############################ Looping functions ############################

def enumerate_column_names_loop(column_clean, all_column):
    for i in range(len(column_clean)):
        key = column_clean[i]
        if key in all_column.keys():
            all_column[key] += 1
        else:
            all_column[key] = 1

def show_best_match_loop(column_names_clean, relevant_columns_cleaned, data_file_name, best_match):
    best_match.loc[data_file_name] = [get_best_candidate_with_levenshtein_distance(col, column_names_clean) for col in relevant_columns_cleaned]

def show_matching_column_loop(data, column_names_clean, data_file_name, relevant_columns_cleaned,column_names):
    perfect_match_indexes = [perfect_match_index(col, column_names_clean) for col in relevant_columns_cleaned]
    perfect_match_columns = [column_names[id] for id in perfect_match_indexes if not id is None]
    temp = data[perfect_match_columns]
    temp.columns = [column_names_clean[id] for id in perfect_match_indexes if not id is None]
    return temp

def show_matching_column_moments_loop(data, column_names_clean, data_file_name, column_names):
    perfect_match_indexes = [perfect_match_index(col, column_names_clean) for col in relevant_columns_cleaned]
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

print("------------- exploring files -------------")

relevant_columns = ['NUMQUEST', 'IDENT', 'ENQU', 'Hors_NK', 'MOUGHATAA', 'COMMUNE',
              'VILLAG0', 'VILLAGE', 'MILIEU', 'NUMEN', 'DATE',
              'CDATSAISIE', 'CODE_ENQ', 'CODE_CONT', 'FCS', 'CSI']
relevant_columns_cleaned = [clean_name(col) for col in relevant_columns if not col is None]

best_match = pd.DataFrame(data = [], columns=relevant_columns_cleaned)
match = pd.DataFrame(data = [], columns=relevant_columns_cleaned)
match_moments = pd.DataFrame(data = [], columns=["variable", "Path", "Mean", "Min", "Q1", "Median" "Q3", "Max"])
all_column = {}
label_name={}

for data_file_index in range(len(data_files_list)):

    print(round(data_file_index/len(data_files_list)*100), " %")

    data_file_name = data_files_list[data_file_index]
    data, meta = convert_data(data_file_name)

    if not meta is None:
        nb_valid_files += 1

        column_names, label_names = meta.column_names, meta.column_labels

        column_names_clean = [clean_name(col) for col in column_names if not col is None]
        column_label_clean = [clean_name(col) for col in label_names if not col is None]
        column_clean = [clean_name(column_names[i]) + ";" + clean_name(label_names[i]) for i in range(len(label_names)) if not label_names[i] is None and not column_names[i] is None]

        ### You can comment if not necessary
        enumerate_column_names_loop(column_clean, all_column)
        show_best_match_loop(column_names_clean, relevant_columns_cleaned, data_file_name, best_match)
        match = match.append(show_matching_column_loop(data, column_names_clean, data_file_name, relevant_columns_cleaned,column_names))
        match_moments = match_moments.append(show_matching_column_moments_loop(data, column_names_clean, data_file_name, column_names))

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
    best_match.to_csv("best_match_column_names.csv", sep=";")

if not match.empty:
    match.reset_index()
    match.to_csv("aggregated_match.csv", sep=";")

if not match_moments.empty:
    match_moments.reset_index()
    match_moments.to_csv("aggregated_match_moments.csv", sep=";")
