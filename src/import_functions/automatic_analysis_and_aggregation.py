from auxiliary_function_for_importing_data import *
from config.aggregation import target_columns


def initialize_relevant_labels(data_files_list, target_columns_cleaned):
    """Fills a dictionnary matching columns with their official name.

    Args:
        data_files_list (list): list of files of which we want to inspect
        the columns from.
        target_columns_cleaned (list): list of clean columns to match.

    Returns:
        relevant_labels_clean (dict): dictionnary matching columns with their
        official name
    """
    matching_dict = {}
    for data_file_index in range(len(data_files_list)):

        print(round(data_file_index / len(data_files_list) * 100), " %")

        data_file_name = data_files_list[data_file_index]
        data, meta = get_data_with_filename(data_file_name)

        if not meta is None:
            column_names, label_names = meta.column_names, meta.column_labels

            column_names_clean = [
                clean(column_names[i])
                for i in range(len(label_names))
                if not label_names[i] is None and not column_names[i] is None
            ]
            column_label_clean = [
                clean(label_names[i])
                for i in range(len(label_names))
                if not label_names[i] is None and not column_names[i] is None
            ]

            perfect_match_indexes = [
                perfect_match_index(col, column_names_clean)
                for col in target_columns_cleaned
            ]
            for id in perfect_match_indexes:
                if not id is None:
                    if column_names_clean[id] in matching_dict.keys():
                        matching_dict[column_names_clean[id]].append(
                            column_label_clean[id]
                        )
                    else:
                        matching_dict[column_names_clean[id]] = [column_label_clean[id]]
    return matching_dict


def count_column_names_loop(column_clean, all_column):
    for i in range(len(column_clean)):
        key = column_clean[i]
        if key in all_column.keys():
            all_column[key] += 1
        else:
            all_column[key] = 1


def get_best_match_with_column_name_loop(
    column_names_clean,
    target_columns_cleaned,
    data_file_name,
    best_match,
    equivalent_columns_table,
):
    """Get best matches for column names.

    Args:
        column_names_clean (str):
        target_columns_cleaned (list): list of cleaned column names.
        data_file_name (str):
        best_match (pd.DataFrame): DataFrame of matches
        equivalent_columns_table (pd.DataFrame):

    """
    best_candidate_by_name_row = []

    for col in target_columns_cleaned:
        to_test = list(set(equivalent_columns_table.loc[:, col])) + [col]
        column_min, distance_min = "", 100
        for col_test in to_test:
            id_name, distance_name = get_best_candidate_with_levenshtein_distance(
                col, column_names_clean
            )
            if distance_name < distance_min:
                distance_min = distance_name
                column_min = column_names_clean[id_name]
        best_candidate_by_name_row.append(column_min + "/" + str(distance_min))

    best_match.loc[data_file_name + "name"] = best_candidate_by_name_row + ["name"]
    return best_match


def get_best_match_with_column_label_loop(
    column_names_clean,
    target_columns_cleaned,
    data_file_name,
    best_match,
    relevant_labels_clean,
    column_label_clean,
):
    """

    Args:
        column_names_clean:
        target_columns_cleaned:
        data_file_name:
        best_match:
        relevant_labels_clean:
        column_label_clean:

    Returns:

    """
    best_candidate_by_label_row = ["" for col in target_columns_cleaned]
    recorded_relevant_labels_clean = list(relevant_labels_clean.keys())

    for i in range(len(target_columns_cleaned)):
        col = target_columns_cleaned[i]
        best_score = 100

        if col in relevant_labels_clean.keys():
            for col_label in relevant_labels_clean[col]:
                id_label, distance_label = get_best_candidate_with_levenshtein_distance(
                    col_label, column_label_clean
                )
                if best_score > distance_label:
                    best_score, best_candidate_by_label_row[i] = (
                        distance_label,
                        column_names_clean[id_label] + "/" + str(distance_label),
                    )

    best_match.loc[data_file_name + "label"] = best_candidate_by_label_row + ["label"]


def generate_best_matches_csv_file(
    data_to_unzip="Mauritania FSMS data.zip",
    target_columns=target_columns,
    home_folder_path=None,
    destination_filename="best_match_for_FSMS_files_columns.csv",
):
    """Function to generate a csv file showing all matching between column names
    for the aggregation.

    Args:
        data_to_unzip (str): name of the zip file.
        target_columns (list): list of target columns, available in config by default.
        home_folder_path (str): path where you store your files.

    """
    if home_folder_path is None:
        home_folder_path = Path.home()
    os.chdir(home_folder_path)
    unzip_data(data_to_unzip)
    data_folder_path = data_to_unzip.split(".")[0]
    data_files_list = get_list_of_data_files(data_folder_path, ".sav")
    nb_valid_files = 0
    equivalent_columns_table = pd.read_csv("columns.csv", sep=";", header=0)  # in drive
    equivalent_columns_table.columns = [
        clean(col) for col in equivalent_columns_table.columns
    ]

    target_columns_cleaned = [clean(col) for col in target_columns if not col is None]

    relevant_labels_clean = initialize_relevant_labels(
        data_files_list, target_columns_cleaned
    )

    all_column = {}
    best_match = pd.DataFrame(
        data=[], columns=target_columns_cleaned + ["matching_type"]
    )
    for data_file_index in range(len(data_files_list)):
        print(round(data_file_index / len(data_files_list) * 100), " %")
        data_file_name = data_files_list[data_file_index]
        data, meta = get_data_with_filename(data_file_name)

        if not meta is None:
            nb_valid_files += 1
            column_names, label_names = meta.column_names, meta.column_labels
            column_names_clean = [clean(col) for col in column_names if not col is None]
            column_label_clean = [clean(col) for col in label_names if not col is None]
            column_clean = [
                clean(column_names[i]) + ";" + clean(label_names[i])
                for i in range(len(label_names))
                if not label_names[i] is None and not column_names[i] is None
            ]
            best_match = get_best_match_with_column_name_loop(
                column_names_clean,
                target_columns_cleaned,
                data_file_name,
                best_match,
                equivalent_columns_table,
            )
    if not best_match.empty:
        best_match.to_csv(destination_filename, sep=";")
