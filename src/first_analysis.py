# -*- coding: utf-8 -*-

import os
from pathlib import Path
import zipfile
import pandas as pd
import numpy as np
import numbers
import re
import matplotlib.pyplot as plt
import pyreadstat


def read_data_file(num):

    home = str(Path.home())

    zip_file = home + "/Mauritania FSMS data.zip"
    root_folder = home + "/Mauritania FSMS data"

    # unzip file
    if not os.path.exists(root_folder):
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(home)

    # list all files in folder
    list_all_files = []
    for path, subdirs, files in os.walk(root_folder):
        for name in files:
            list_all_files.append(os.path.join(path, name))

    # list data files
    list_data_file = [f for f in list_all_files if re.search(".sav$", f)]

    # read data
    data, meta = pyreadstat.read_sav(list_data_file[num], apply_value_formats=True)

    return (data, meta)


data, meta = read_data_file(0)

# columns description
columns = pd.DataFrame({"variable": meta.column_names, "label": meta.column_labels})

# rename columns
fakedata = data.rename(columns={"IDENT": "ID", "DATE": "TIME"})
# column used as identifier
columns_id = [
    "Q_10_NUMQUEST",
    "IDENT",
    "ENQU",
    "Hors_NK",
    "Q_12_Moughataa",
    "13_Commune",
    "VILLAG0",
    "VILLAGE",
    "Q_15_MILIEU",
    "NUMEN",
    "DATE",
    "CDATSAISIE",
    "CODE_ENQ",
    "CODE_CONT",
]

# variable of interest
columns_value = [col for col in data.columns if col not in columns_id]
columns_value = ["FCS", "CSI"]

df = pd.melt(data, id_vars=columns_id, value_vars=columns_value)
df = df.merge(columns, on="variable", how="left")


