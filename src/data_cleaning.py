from Mauritania_FSMS_aggregation import get_list_of_data_files
import pyreadstat
import pandas as pd


list_file = get_list_of_data_files()
data, meta = pyreadstat.read_sav(
    list_file[0], apply_value_formats=True, encoding="ISO-8859-1"
)
columns = pd.DataFrame({"variable": meta.column_names, "label": meta.column_labels})
