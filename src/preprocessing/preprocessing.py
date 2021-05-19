import pandas as pd
import seaborn
import sklearn
import geopandas as gpd
import missingno as msno
import seaborn as sns
import numpy as np
from pathlib import Path
from config.preprocessing import preprocessing_FSMS_files_with_yields_types, education_level_standardization_origin, \
    education_level_standardization_match


def preprocess_FSMS_files_with_yields(
    home_path = None,
    csv_file = "/aggregated_match_for_FSMS_files_with_yields.csv",
):
    """Change types, drop unnecessary columns, etc... to work with the data.

    Args:
        path_to_file (str): path to the file

    Returns:
        df_aggregated_file (pd.DataFrame): preprocessed dataframes
    """
    if home_path is None:
        home_path = str(Path.home())
    path_to_file = home_path+csv_file
    df_aggregated_file = pd.read_csv(path_to_file, low_memory=False)
    df_aggregated_file.drop(columns=["Unnamed: 0"], inplace=True)
    columns = []
    for col in df_aggregated_file.columns.to_list():
        new_col = col.replace("$", "")
        columns.append(new_col)
    df_aggregated_file.columns = columns
    df_aggregated_file = df_aggregated_file.astype(
        preprocessing_FSMS_files_with_yields_types
    )
    df_aggregated_file["Scol"]=standardize_education_level(df_aggregated_file["Scol"])
    df_aggregated_file = df_aggregated_file.drop(columns=["cdatsaisie"])
    df_aggregated_file["date"] = df_aggregated_file["date"].apply(lambda row: standardize_date(row))
    df_aggregated_file["date"] = pd.to_datetime(df_aggregated_file["date"], format="%Y-%m-%d", errors='coerce')
    return df_aggregated_file


def standardize_education_level(education_column):
    education_column = education_column.replace(education_level_standardization_origin, education_level_standardization_match)
    education_column = pd.to_numeric(education_column, errors='coerce')
    return education_column


def standardize_date(date):
    if "-" in date:
        return date
    else:
        if len(date)>6:
            date_tmp = date.split(".")[0]
            year = date_tmp[-4:]
            month = date_tmp[-6:-4]
            day = date_tmp[:-6]
            if len(day)==1:
                day="0"+day
            return year+"-"+month+"-"+day
        else:
            return np.nan

if __name__=="__main__":
    preprocess_FSMS_files_with_yields()

