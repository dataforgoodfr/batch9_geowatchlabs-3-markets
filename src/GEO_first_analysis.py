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



from osgeo import gdal, ogr, osr

raster=file
ds=gdal.Open(raster)

ext=GetExtent(ds)

src_srs=osr.SpatialReference()
src_srs.ImportFromWkt(ds.GetProjection())
#tgt_srs=osr.SpatialReference()
#tgt_srs.ImportFromEPSG(4326)
tgt_srs = src_srs.CloneGeogCS()

geo_ext=ReprojectCoords(ext, src_srs, tgt_srs)