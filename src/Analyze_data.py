# -*- coding: utf-8 -*-

############################ Import libraries ############################

from Auxiliary_function_for_importing_data import *

############################ code ############################

unzip_data("Mauritania FSMS data")

print("------------- data unzipped ---------------")

data_files_list = get_list_of_data_files("Mauritania FSMS data", ".sav")

print("------------- choose file -----------------")

print("\n")

nb_file = 0
for file_name in data_files_list:
    print(nb_file, file_name.split("/")[-1])
    nb_file += 1

print("\n")

nb_file = int(input("Select file number to export: "))

print("\n")
print("------------- exporting file -----------------")

data, meta = get_data_with_filename(data_files_list[nb_file])

meta_pd = pd.DataFrame(data = [meta.column_labels], columns = meta.column_names)

meta_pd.to_csv("meta_" + data_files_list[nb_file].split("\\")[-1][:-4] + ".csv")
data.to_csv("data_" + data_files_list[nb_file].split("\\")[-1][:-4] + ".csv")
