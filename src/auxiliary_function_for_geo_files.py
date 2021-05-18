import os
import re
from pathlib import Path
import zipfile
import pandas as pd
from osgeo import osr
from auxiliary_function_for_importing_data import extract_pattern_from_string as matching
from osgeo import gdal
import matplotlib.pyplot as plt


def list_geo_file(folder=""):
    """ Lists all the files in the folder named "folder"
    contained in GeoWatch Labs Agricultural Maps.

    Args:
        folder (str): folder name in which to search in GeoWatch Labs Agricultural
        Maps folder.

    Returns:
        list_data_file (list): list of files in GeoWatch Labs Agricultural Maps
    """
    home = str(Path.home())

    zip_file = home + "/GeoWatch Labs Agricultural Maps.zip"
    root_folder = home + "/GeoWatch Labs Agricultural Maps/" + folder

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
    list_data_file = [f for f in list_all_files if re.search(".tif$", f)]

    return list_data_file


def df_geo_file():
    """ Build geo file DataFrame of yields.

    Returns:
        files (pd.DataFrame): dataframe of yields, year, zone.
    """
    list_crop = ["cowpea", "groundnut", "maize", "millet", "sorghum"]
    list_year = [str(n) for n in range(2010, 2015)]
    list_zone = ["zone1_" + str(i) for i in list(range(0, 14))][::-1]

    def class_year(string, pattern=list_year):
        return matching(string, list_year)

    def class_zone(string, pattern=list_zone):
        return matching(string, pattern)

    def class_crop(string, pattern=list_crop):
        return matching(string, pattern)

    list_geomap = list_geo_file("Crop mapping")
    geomap_df = pd.DataFrame({"geomap_file": list_geomap})
    geomap_df["zone"] = geomap_df["geomap_file"].apply(class_zone)

    list_yield_file = list_geo_file("Historical Yields")

    yield_df = pd.DataFrame({"yield_file": list_yield_file})

    yield_df["year"] = yield_df["yield_file"].apply(class_year)
    yield_df["crop"] = yield_df["yield_file"].apply(class_crop)
    yield_df["zone"] = yield_df["yield_file"].apply(class_zone)

    files = yield_df.merge(geomap_df, on="zone", how="left")

    return files


def read_geo_file(file):
    """ Visualize tiff file.

    Args:
        file (str): ,ame of the tiff file to visualize.

    Returns:
        arr (np.array): numpy array of the tiff
    """

    gdal_data = gdal.Open(file, gdal.GA_ReadOnly)
    band = gdal_data.GetRasterBand(1)
    arr = band.ReadAsArray()
    plt.imshow(arr)
    return arr


def get_extent(ds):
    """ Return list of corner coordinates from a gdal Dataset """
    xmin, xpixel, _, ymax, _, ypixel = ds.GetGeoTransform()
    width, height = ds.RasterXSize, ds.RasterYSize
    xmax = xmin + width * xpixel
    ymin = ymax + height * ypixel

    return (xmin, ymax), (xmax, ymax), (xmax, ymin), (xmin, ymin)


def reproject_coords(coords, src_srs, tgt_srs):
    """ Reproject a list of x,y coordinates. """
    trans_coords = []
    transform = osr.CoordinateTransformation(src_srs, tgt_srs)
    for x, y in coords:
        x, y, z = transform.TransformPoint(x, y)
        trans_coords.append([x, y])
    return trans_coords
