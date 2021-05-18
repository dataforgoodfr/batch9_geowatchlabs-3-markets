"""
This code aims as reading .sav data, merging it together,
then saving it as csv.
"""

from auxiliary_function_for_importing_data import *

if __name__ == "__main__":
    unzip_data("Mauritania FSMS data")
    data_files_list = get_list_of_data_files("Mauritania FSMS data", ".sav")
    nb_file = 0
    for file_name in data_files_list:
        nb_file += 1
    data, meta = get_data_with_filename(data_files_list[nb_file])
    meta_pd = pd.DataFrame(data=[meta.column_labels], columns=meta.column_names)
    meta_pd.to_csv("meta_" + data_files_list[nb_file].split("\\")[-1][:-4] + ".csv")
    data.to_csv("data_" + data_files_list[nb_file].split("\\")[-1][:-4] + ".csv")
