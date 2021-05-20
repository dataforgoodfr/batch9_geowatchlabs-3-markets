import pandas as pd
import seaborn
import sklearn
import geopandas as gpd
import missingno as msno
import seaborn as sns
import numpy as np
from pathlib import Path
from config.preprocessing import (
    preprocessing_FSMS_files_with_yields_types,
    education_level_standardization_origin,
    education_level_standardization_match,
)


def preprocess_FSMS_files_with_yields(
    home_path=None,
    csv_file="/aggregated_match_for_FSMS_files_with_yields_with_price.csv",
):
    """Change types, drop unnecessary columns, etc... to work with the data.

    Args:
        path_to_file (str): path to the file

    Returns:
        df_aggregated_file (pd.DataFrame): preprocessed dataframes
    """
    if home_path is None:
        home_path = str(Path.home())
    path_to_file = home_path + csv_file
    df_aggregated_file = pd.read_csv(path_to_file, low_memory=False)
    df_aggregated_file.drop(columns=["Unnamed: 0", "Unnamed: 0.1"], inplace=True)
    columns = []
    for col in df_aggregated_file.columns.to_list():
        new_col = col.replace("$", "")
        columns.append(new_col)
    df_aggregated_file.columns = columns
    df_aggregated_file = df_aggregated_file.astype(
        preprocessing_FSMS_files_with_yields_types
    )
    df_aggregated_file = df_aggregated_file.rename(
        columns={"id": "price_id"}
    )  # je l'ai gardé mais je pense à supprimer + tard

    df_aggregated_file["Scol"] = standardize_education_level(df_aggregated_file["Scol"])
    df_aggregated_file["Tailmen"] = df_aggregated_file["Tailmen"].apply(
        lambda row: standardize_tailmen(row)
    )
    df_aggregated_file = df_aggregated_file.drop(
        columns=["cdatsaisie"]
    )  # we don't need it, c'est la date de saisie
    df_aggregated_file["date"] = df_aggregated_file["date"].apply(
        lambda row: standardize_date(row)
    )
    df_aggregated_file["date"] = pd.to_datetime(
        df_aggregated_file["date"], format="%Y-%m-%d", errors="coerce"
    )
    return df_aggregated_file


def standardize_education_level(education_column):
    """This function aims at standardizing the education level. The column
    has mixed types (ints and categories, with overlapping categories).

    Args:
        education_column (pd.Series): column in which we will replace the identified
        matching values.

    Returns:
        education_column (pd.Series): standardized column
    """
    education_column = education_column.replace(
        education_level_standardization_origin, education_level_standardization_match
    )
    education_column = pd.to_numeric(education_column, errors="coerce")
    return education_column


def standardize_tailmen(tailmen):
    """This function aims at standardizing the household size. The column
    has mixed types (ints and strings).

    Args:
        tailmen (str): household size as recorded, can be category (1 to 4 people)
        or float (4.0 = there are 4 people in the household).

    Returns:
        tailmen (str): only categories
    """
    if len(tailmen) < 5:
        count_tailmen = float(tailmen)
        if count_tailmen < 5:
            tailmen = "1 à 4 personnes"
            return tailmen
        elif count_tailmen < 9 and count_tailmen >= 5:
            tailmen = "5 à 8 personnes"
            return tailmen
        elif count_tailmen < 13 and count_tailmen >= 9:
            tailmen = "9 à 12 personnes"
            return tailmen
        else:
            tailmen = "13 personnes et plus"
            return tailmen
    else:
        return tailmen


def standardize_date(date):
    """This function aims at standardizing the date. There are several ways of
    displaying the date in the column.

    Args:
        date (str): date as recorded in the column.

    Returns:
        date (str): standardized date (YYYY-MM-DD).
    """
    if "-" in date:
        return date
    else:
        if len(date) > 6:
            date_tmp = date.split(".")[0]
            year = date_tmp[-4:]
            month = date_tmp[-6:-4]
            day = date_tmp[:-6]
            if len(day) == 1:
                day = "0" + day
            return year + "-" + month + "-" + day
        else:
            return np.nan


if __name__ == "__main__":
    preprocess_FSMS_files_with_yields()
