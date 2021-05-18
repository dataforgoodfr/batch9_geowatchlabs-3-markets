import pandas as pd
import seaborn
import sklearn
import geopandas as gpd
import missingno as msno
import seaborn as sns
from pathlib import Path
from config.preprocessing import preprocessing_FSMS_files_with_yields_types


def preprocess_FSMS_files_with_yields(
    path_to_file=Path.home() + "/aggregated_match_for_FSMS_files_with_yields.csv",
):
    """Change types, drop unnecessary columns, etc... to work with the data.

    Args:
        path_to_file (str): path to the file

    Returns:
        df_aggregated_file (pd.DataFrame): preprocessed dataframes
    """
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
    return df_aggregated_file
