# -*- coding: utf-8 -*-

############################ Import libraries ############################

import zipfile
import pandas as pd
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
    if str(name) != "nan":
        #seperate in words
        name_lowercase = name.lower()
        relevant_words = re.findall(r'[a-z]+', name_lowercase)

        #remove one letter words
        relevant_words = [word for word in relevant_words if len(word) > 1]

        relevant_sentence = " ".join(relevant_words)
        return relevant_sentence
    else:
        return None

def get_best_candidate_with_levenshtein_distance(match_name, candidates_name):
    distance_by_candidate = [jellyfish.levenshtein_distance(match_name, candidate) for candidate in candidates_name]
    distance_min = min(distance_by_candidate)

    return distance_by_candidate.index(distance_min), distance_min

def perfect_match_index(match_name, candidates_name):
    try:
        return candidates_name.index(match_name)
    except:
        return None

def export_data(file_name):
    data, meta = get_data_with_filename(file)
    data.to_csv("file_name".split("/")[-1][:-4] + ".csv")
    meta.to_csv("file_name".split("/")[-1][:-4] + ".csv")

def extract_pattern_from_string(string, pattern):
        for pat in pattern:
            if re.search(pat, string):
                return(pat)
                                
def extract_year_from_filename(filename):
    list_year = [str(n) for n in range(2010, 2016)]
    return(extract_pattern_from_string(filename, pattern = list_year))

def extract_month_from_filename(filename):
    list_year = ['Decembre', 'Janvier', 'Juillet', 'Juin']
    return(extract_pattern_from_string(filename, pattern = list_year))
    
        
        


