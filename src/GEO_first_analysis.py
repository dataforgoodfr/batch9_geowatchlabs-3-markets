# -*- coding: utf-8 -*-

import os
from pathlib import Path
import zipfile
import pandas as pd
import numpy as np
import numbers
import re, osgeo
import matplotlib.pyplot as plt
import pyreadstat

from Auxiliary_function_for_geo_files import *

# list of all files
files = df_geo_file()

# select one specific file 
data_2010_groundnut = files[(files['crop'] == 'groundnut') &
                            (files['year'] == '2010')].reset_index(drop=True)

file = data_2010_groundnut.geomap_file[4]

#read the file
arr = read_geo_file(file)

