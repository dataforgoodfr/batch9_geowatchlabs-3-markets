from import_functions.auxiliary_function_for_importing_data import *
import numpy as np

from import_functions.import_prices import import_prices
from import_functions.import_yields import import_commune_yields, join_yields

"""
Uses common matching work on columns through years to match them.
"""


def aggregate_matching_column_loop(
    data, column_names, data_file_name, eq_target_column, target_columns
):
    """Returns a DataFrame containing only columns we could match with their official name.

    Args:
        data (pd.DataFrame): DataFrame of current inspected file.
        column_names (list of str): list of column names from the metadata DataFrame
        data_file_name (str): name of the file currently inspected
        eq_target_column (list of str): list of column names that match official column names
        target_columns (list of str): list of official column names

    Returns:
        temp (pd.DataFrame): DataFrame containing only columns we could match with their official name
    """
    perfect_match_indexes = [
        perfect_match_index(col, column_names)
        for col in eq_target_column
        if not col is None
    ]
    perfect_match_columns = [
        column_names[id] for id in perfect_match_indexes if not id is None
    ]
    temp = data[perfect_match_columns]
    temp.columns = [
        target_columns[i]
        for i in range(len(eq_target_column))
        if not eq_target_column[i] is None
        and not perfect_match_index(eq_target_column[i], column_names) is None
    ]
    temp["Path"] = data_file_name
    return temp


def aggregate_matching_column_moments_loop(
    data, column_names, data_file_name, eq_target_column, target_columns
):
    perfect_match_indexes = [
        perfect_match_index(col, column_names) for col in eq_target_column if col != ""
    ]
    temp = pd.DataFrame(
        data=[], columns=["variable", "Path", "Mean", "Min", "Q1", "Median" "Q3", "Max"]
    )
    for i in range(len(perfect_match_indexes)):
        id = perfect_match_indexes[i]
        if not id is None:
            col = column_names[id]
            if data[col].dtypes.kind in "fi":
                temp = temp.append(
                    pd.DataFrame(
                        {
                            "variable": [target_columns[i]],
                            "Path": [data_file_name],
                            "Mean": [np.mean(data[col])],
                            "Min": [np.min(data[col])],
                            "Q1": [np.quantile(data[col], 0.25, axis=0)],
                            "Median": [np.median(data[col])],
                            "Q3": [np.quantile(data[col], 0.75, axis=0)],
                            "Max": [np.max(data[col])],
                        }
                    )
                )
    return temp


def import_dataset(
    home_folder_path=None,
    mauritania_FSMS_data_zipfile="Mauritania FSMS data",
    columns_csv_path="columns.csv",
    path_to_population_image="Groupe 3 - Marchés Alimentaires/images/population images",
    path_to_wfp_food_prices_mauritania_csv="Groupe 3 - Marchés Alimentaires/prix/wfp_food_prices_mauritania.csv",
    historical_data_files_path="GeoWatch Labs Agricultural Maps/Historical Yields",
):
    if home_folder_path is None:
        home_folder_path = Path.home()
    #os.chdir(home_folder_path)
    unzip_data(mauritania_FSMS_data_zipfile)
    data_files_list = get_list_of_data_files(mauritania_FSMS_data_zipfile, ".sav")
    nb_valid_files = 0

    equivalent_columns_table = pd.read_csv(columns_csv_path, sep=",", header=0)
    target_columns = [
        col for col in equivalent_columns_table.columns if str(col) != "nan"
    ]

    match = pd.DataFrame(data=[], columns=target_columns)
    match_moments = pd.DataFrame(
        data=[], columns=["variable", "Path", "Mean", "Min", "Q1", "Median" "Q3", "Max"]
    )

    for data_file_index in range(len(data_files_list)):
        print(round(data_file_index / len(data_files_list) * 100), " %")
        data_file_name = data_files_list[data_file_index]
        data, meta = get_data_with_filename(data_file_name)

        if not meta is None:
            nb_valid_files += 1

            column_names = [col for col in meta.column_names if not col is None]
            eq_target_columns = [
                equivalent_columns_table.loc[data_file_index, col]
                for col in target_columns
            ]
            match = match.append(
                aggregate_matching_column_loop(
                    data,
                    column_names,
                    data_file_name,
                    eq_target_columns,
                    target_columns,
                )
            )
            match_moments = match_moments.append(
                aggregate_matching_column_moments_loop(
                    data,
                    column_names,
                    data_file_name,
                    eq_target_columns,
                    target_columns,
                )
            )

    match["year"] = match["Path"].apply(extract_year_from_filename)
    match["month"] = match["Path"].apply(extract_month_from_filename)

    historical_data_files_list = get_list_of_data_files(
        historical_data_files_path, ".tif"
    )
    commune_to_yield_avg_by_year_by_crop, commune_dict = import_commune_yields(
        historical_data_files_list, path_to_population_image
    )

    match = join_yields(match, commune_to_yield_avg_by_year_by_crop, commune_dict)
    
    clean_moughataa_column(match, commune_dict)
    
    match = import_prices(
        match,
        path_to_wfp_food_prices_mauritania_csv,
    )

    if not match.empty:
        match.reset_index()
        match.to_csv(
            "aggregated_match_for_FSMS_files_with_yields_with_price.csv",
            sep=",",
            index=False,
        )
        return match
    if not match_moments.empty:
        match_moments.reset_index()
        match_moments.to_csv(
            "aggregated_match_moments_for_FSMS_files.csv", sep=",", index=False
        )
