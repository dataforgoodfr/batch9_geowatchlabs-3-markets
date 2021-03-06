import zipfile
import pandas as pd
import re
import pyreadstat
import os
import os.path
from pathlib import Path
import errno
import jellyfish
import json
import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

def clean_gps_coord(gps_coord_str):
    """This function aims at converting gps coords string to gps coords

    Args:
        gps_coord_str (str): string of gps coords

    """
    gps_coord_str_clean = gps_coord_str.replace('&lt;Point&gt;&lt;coordinates&gt;','')
    gps_coord_str_clean = gps_coord_str_clean.replace('&lt;/coordinates&gt;&lt;/Point&gt;','')
    return gps_coord_str_clean

def extract_lat_lon(gps_coord_str):
     """This function aims at converting gps coords string to lan & lat

      Args:
         gps_coord_str (str): string of gps coords

     """
     lon = gps_coord_str.split(',', 2)[0]
     lat = gps_coord_str.split(',', 2)[1]
     return lat, lon

def unzip_data(folder_name):
    """This function aims at unzipping data in folder with folder_name.

    Args:
        folder_name (str): name of the folder to unzip.

    """
    current_directory = os.getcwd()
    pre_folder_name = folder_name.split(".")[0]
    if os.path.exists(current_directory + "/" + pre_folder_name):
        print("File has already been extracted.")
    else:
        correct_zip_file = [
            f
            for f in os.listdir(current_directory)
            if f[: len(folder_name)] == folder_name
        ]
        if len(correct_zip_file) == 0:
            print(
                FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), folder_name + "%%%%.zip"
                )
            )
        else:
            zip_file = os.path.join(current_directory, correct_zip_file[-1])
            root_folder = os.path.join(current_directory, folder_name)

            if not os.path.exists(root_folder):
                with zipfile.ZipFile(zip_file, "r") as zip_ref:
                    zip_ref.extractall(current_directory)
            else:
                print(f"Cannot extract zipfile at {root_folder}")


def get_list_of_data_files(folder_name, extension):
    """Get list of data files in folder name with the specified extension.

    Args:
        folder_name (str): name of the folder to look into.
        extension (str): extension of the files we are looking for.

    Returns:
        list_data_file (list of str): list of the filenames.
    """
    current_directory = os.getcwd()
    root_folder = os.path.join(current_directory, folder_name)

    # list all files in folder
    list_all_files = []
    for path, subdirs, files in os.walk(root_folder):
        for name in files:
            list_all_files.append(os.path.join(path, name))

    # list data files
    list_data_file = np.array([f for f in list_all_files if re.search(extension + "$", f)])
    
    #sort by date
    list_data_file_date = np.array([str(extract_year_from_filename(f)) + str(extract_month_from_filename(f)) for f in list_data_file])
    inds = list_data_file_date.argsort()
    list_data_file_sorted = list(list_data_file[inds])
    return list_data_file_sorted


def get_data_with_filename(file):
    """Get metadata and data from the .sav file.

    Args:
        file (str): .sav filename.

    Returns:
        data, meta (tuple): data
    """
    try:
        data, meta = pyreadstat.read_sav(
            file, apply_value_formats=True, encoding="ISO-8859-1"
        )
        return data, meta
    except FileNotFoundError as FE:
        print("Need to investigate ", file)
        return None, None


def clean(name):
    """Clean name by only keeping the key-words in it.

    Args:
        name (str): name we are cleaning.

    Returns:
        relevant_sentence (str): cleaned name
    """
    if str(name) != "nan":
        # seperate in words
        name_lowercase = name.lower()
        relevant_words = re.findall(r"[a-z]+", name_lowercase)

        # remove one letter words
        relevant_words = [word for word in relevant_words if len(word) > 1]

        relevant_sentence = " ".join(relevant_words)
        return relevant_sentence
    else:
        return None


def get_best_candidate_with_levenshtein_distance(match_name, candidates_name):
    """Match strings based on levenshtein distance.

    Args:
        match_name (str): word to match.
        candidates_name (str): candidate words for matching.

    Returns:
        best_candidate, distance_min (tuple): closest word, and their levenshtein
        distance to the original one.
    """
    distance_by_candidate = [
        jellyfish.levenshtein_distance(match_name, candidate)
        for candidate in candidates_name
    ]
    distance_min = min(distance_by_candidate)
    best_candidate = distance_by_candidate.index(distance_min)
    return best_candidate, distance_min


def perfect_match_index(match_name, candidates_name):
    """Returns the index of the perfect match.

    Args:
        match_name (str): name to match.
        candidates_name (list): list of candidates.

    Returns:
        match_index (int): index of match
    """
    try:
        match_index = candidates_name.index(match_name)
        return match_index
    except:
        return None


def export_data(file_name):
    """Export data and metadata to csv.

    Args:
        file_name (str): .sav filename.

    """
    data, meta = get_data_with_filename(file_name)
    data.to_csv("file_name".split("/")[-1][:-4] + ".csv")
    meta.to_csv("file_name".split("/")[-1][:-4] + ".csv")


def extract_pattern_from_string(string, pattern):
    """Extract pattern from string through regex.

    Args:
        string (str): string in which to search for the pattern
        pattern (list): list of patterns to test in string

    Returns:
        pat (str): pattern in the string
    """
    for pat in pattern:
        if re.search(pat, string):
            return pat


def extract_year_from_filename(filename):
    """Extract year from filename with regex.

    Args:
        filename (str): file name we want to extract year from.

    Returns:
        year (str): year pattern extracted from filename.
    """
    list_year = [str(n) for n in range(2010, 2016)]
    return extract_pattern_from_string(filename, pattern=list_year)

def extract_month_number_from_filename(filename):
    """Extract month number from filename with regex.

    Args:
        filename (str): file name we want to extract month from.

    Returns:
        month (str): month pattern extracted from filename.
    """
    list_month = ["Decembre", "Janvier", "Juillet", "Juin"]
    month2nb = {"Decembre": "12", "Janvier": "01", "Juillet" : "07", "Juin" : "06"}
    
    month = extract_pattern_from_string(filename, pattern=list_month)
    
    if month is not None: 
        return month2nb[month]
    else:
        return "13"


def extract_month_from_filename(filename):
    """Extract month from filename with regex.

    Args:
        filename (str): file name we want to extract month from.

    Returns:
        month (str): month pattern extracted from filename.
    """
    list_month = ["Decembre", "Janvier", "Juillet", "Juin"]
    return extract_pattern_from_string(filename, pattern=list_month)


def clean_name(name):
    """Clean name by removing spaces, underscore, 2 and ??ne

    Args:
        name (str): name we are cleaning.

    Returns:
        name (str): cleaned name
    """

    return name.lower().replace(" ","").replace("_","").replace("??ne", "en").replace("2", "")


def get_real_name(moughataa, commune_dict):
    """get cleaned moughataa name if indice

    Args:
        moughataa (unknown): can be name of moughataa or indice in float or string of float

    Returns:
        name (str): actual cleaned moughataa name
    """
    if str(moughataa) == "nan":
        return ""
    elif str(type(moughataa)) == "<class 'float'>":
        return clean_name(commune_dict[int(moughataa)])
    elif "." in moughataa:
        return clean_name(commune_dict[int(float(moughataa))])
    else:
        return clean_name(moughataa)


def clean_moughataa_column(data, commune_dict):
    """clean moughataa column
    Args:
        data (dataframe): dataframe of data with a moughataa column
        commune_dict(int: string): dictionary indice: actual moughataa
    Returns:
        name (str): actual cleaned moughataa name
    """
    with open("Communes.geojson") as json_file:
        temp = json.load(json_file)

    commune_dict = {
        int(commune['properties']['ID_3']) : clean_name(commune['properties']['ADM3_REFNA'])
        for commune in temp['features']
    }

    data["moughataa"] = [get_real_name(name, commune_dict) for name in data["moughataa"]]


def get_moughataa_wilaya():
    """Get commmune.geojson data.

    Returns:
        commune_dict, commune_id, geometry (tuple): commmune.geojson data
    """
    try:
        with open("Moughataas_new.geojson") as json_file:
            data = json.load(json_file)

        wilayas = [commune["properties"]["NAME_1"] for commune in data["features"]]
        moughataas = [commune["properties"]["NAME_2"] for commune in data["features"]]
        geometry = [
            Polygon(commune["geometry"]["coordinates"][0][0])
            for commune in data["features"]
        ]

        return wilayas, moughataas, geometry

    except:
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), "Moughataas_new.geojson"
        )

def fill_moughtaa_wilaya(df):
    """This function aims at filling missing moughataa and wilaya values.
    If moughataa/wilaya is missing, then we impute it from the lat-lon.

    Args:
        df (pd.DataFrame): DataFrame we want to impute the values in.

    Returns:
        df (pd.DataFrame): filled DataFrame.
    """
    
    wilayas, moughataas, geometry = get_moughataa_wilaya()
    
    for i in df[pd.isna(df[["moughataa","wilaya"]]).any(1)].index:
        lat = df.loc[i,"latitude"]
        lon = df.loc[i,"longitude"]

        if not pd.isna(lat) and not pd.isna(lon):
            point = Point(float(lon), float(lat))
            
            found = False
            
            for moughataa_id in range(len(geometry)):
                moughataa = geometry[moughataa_id]
                
                if moughataa.contains(point):
                    found = True
                    matching_moughataa_id = moughataa_id
                    break
                
            if found:
                df.loc[i,"moughataa"] = moughataas[matching_moughataa_id]
                df.loc[i,"wilaya"] =wilayas[matching_moughataa_id]
    
    return df