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


def preprocess_FSMS_files_with_yields_and_prices(
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

    if "Unnamed: 0" in df_aggregated_file.columns:
        df_aggregated_file.drop(columns=["Unnamed: 0"], inplace=True)
    if "Unnamed: 0.1" in df_aggregated_file.columns:
        df_aggregated_file.drop(columns=["Unnamed: 0.1"], inplace=True)

    columns = []
    for col in df_aggregated_file.columns.to_list():
        new_col = col.replace("$", "")
        columns.append(new_col)

    df_aggregated_file.columns = columns
    try:
        df_aggregated_file = df_aggregated_file.astype(
            preprocessing_FSMS_files_with_yields_types
        )
    except:
        pass
    df_aggregated_file = df_aggregated_file.rename(columns={"id": "price_id"})

    df_aggregated_file["Scol"] = standardize_education_level(df_aggregated_file["Scol"])
    try:
        df_aggregated_file["Tailmen_range"] = df_aggregated_file["Tailmen"].apply(
            lambda row: standardize_tailmen(row)
        )
    except:
        pass
    try:
        df_aggregated_file = df_aggregated_file.drop(columns=["cdatsaisie"])
        df_aggregated_file["date"] = df_aggregated_file["date"].apply(
            lambda row: standardize_date(row)
        )
    except:
        pass
    try:
        df_aggregated_file["date"] = pd.to_datetime(
            df_aggregated_file["date"], format="%Y-%m-%d", errors="coerce"
        )
        df_aggregated_file = fill_lat_lon(df_aggregated_file)
    except:
        pass
    return df_aggregated_file


def geospatial_match_dataframe(df):
    """Create a DataFrame to match communes+moughataas+latitude+longitude+altitude.

    Args:
        df (pd.DataFrame): original DataFrame, to compute the matching table from.

    Returns:
        commune_geo_table (pd.DataFrame): matching DataFrame.
    """
    commune_geo_table = pd.DataFrame(
        df[["commune", "latitude", "longitude", "Altitude"]]
        .groupby(by=["commune"])
        .mean()
    ).reset_index()
    moughataa_geo_table = pd.DataFrame(
        df[["moughataa", "latitude", "longitude", "Altitude"]]
        .groupby(by=["moughataa"])
        .mean()
    ).reset_index()

    moughataas_communes = (
        df[["commune", "moughataa"]].drop_duplicates().set_index("commune")
    )
    moughataas_communes_match_dict = moughataas_communes.to_dict()["moughataa"]
    commune_geo_table["moughataa"] = commune_geo_table["commune"].apply(
        lambda row: moughataas_communes_match_dict[row]
    )
    commune_geo_table = commune_geo_table.merge(
        moughataa_geo_table, on="moughataa", how="left", suffixes=("", "_moughataa")
    )
    commune_geo_table["latitude"] = commune_geo_table["latitude"].fillna(
        commune_geo_table["latitude_moughataa"]
    )
    commune_geo_table["longitude"] = commune_geo_table["longitude"].fillna(
        commune_geo_table["longitude_moughataa"]
    )
    commune_geo_table["Altitude"] = commune_geo_table["Altitude"].fillna(
        commune_geo_table["Altitude_moughataa"]
    )
    commune_geo_table = commune_geo_table.drop(
        columns=["latitude_moughataa", "longitude_moughataa", "Altitude_moughataa"]
    )
    return commune_geo_table


def fill_lat_lon(df):
    """This function aims at filling missing lat-lon and altitude values.
    If lat-long is missing, then we impute the average lat-lon of the commune.
    If the lat-long is missing in the commune, we impute the average lat-lon
    of the moughataa.

    Args:
        df (pd.DataFrame): DataFrame we want to impute the values in.

    Returns:
        df (pd.DataFrame): filled DataFrame.
    """
    df_geo_match = geospatial_match_dataframe(df)
    df = df.merge(df_geo_match, how="left", on="commune", suffixes=("", "_geomatch"))
    df["latitude"] = df["latitude"].fillna(df["latitude_geomatch"])
    df["longitude"] = df["longitude"].fillna(df["longitude_geomatch"])
    df["Altitude"] = df["Altitude"].fillna(df["Altitude_geomatch"])
    df = df.drop(
        columns=["latitude_geomatch", "longitude_geomatch", "Altitude_geomatch"]
    )
    return df


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


def standardize_bool_hors_nk(hors_nk_str):
    """This column contains string while it could be a boolean. To ease future data manipulation,
    let's convert it to a boolean, with a value of 1 if the data is not in Nouakchott, and 0 is the
    data is from Nouakchott. It returns None if we can't recognize the string in argument.

    Args:
        hors_nk_str (str): string in the column

    Returns:
        boolean (int): 0 or 1.
    """
    if hors_nk_str == "Hors Nouakchott":
        return 1
    if hors_nk_str == "Nouakchott":
        return 0
    else:
        return None


def standardize_moughataa_commune_float(str_name):
    """Checks if the name could be a float by trying to cast it.
    If it is, then we must replace the value by None.

    Args:
        str_name (str): name of the moughataa or commune.

    Returns:
        str_name (str): original name or None.
    """
    try:
        float_name = float(str_name)
        return None
    except Exception as e:
        return str_name


if __name__ == "__main__":
    df = preprocess_FSMS_files_with_yields_and_prices()
    df.to_csv("./standardized_aggregated_dataset.csv")
