import numpy as np
import gdal
import json
import rasterio
from rasterio.features import rasterize
import zipfile
import pandas as pd
import re
import os
import os.path
from pathlib import Path
import errno
from shapely.geometry import Polygon
from scipy.special import expit


def get_list_of_data_files(folder_name, extension):
    """Get list of data files in folder name with the specified extension.

    Args:
        folder_name (str): name of the folder to look into.
        extension (str): extension of the files we are looking for.

    Returns:
        list_data_file (list of str): list of the filenames.
    """
    current_directory = str(Path().absolute())

    root_folder = os.path.join(current_directory, folder_name)

    # list all files in folder
    list_all_files = []
    for path, subdirs, files in os.walk(root_folder):
        for name in files:
            list_all_files.append(os.path.join(path, name))

    # list data files
    list_data_file = [f for f in list_all_files if re.search(extension + "$", f)]

    return list_data_file


def open_communes():
    """Get commmune.geojson data.

    Returns:
        commune_dict, commune_id, geometry (tuple): commmune.geojson data
    """
    try:
        with open("Communes.geojson") as json_file:
            data = json.load(json_file)

        commune_id = [commune["properties"]["ID_3"] for commune in data["features"]]
        commune_dict = {
            commune["properties"]["ADM3_REFNA"]: commune["properties"]["ID_3"]
            for commune in data["features"]
        }
        geometry = [
            Polygon(commune["geometry"]["coordinates"][0][0])
            for commune in data["features"]
        ]

        return commune_dict, commune_id, geometry

    except:
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), "Communes.geojson"
        )


def get_extent(ds):
    """ Returns the bounding box of tiff image. """
    geo_t = ds.GetGeoTransform()
    x_size, y_size = ds.RasterXSize, ds.RasterYSize
    xmin = min(geo_t[0], geo_t[0] + x_size * geo_t[1])
    xmax = max(geo_t[0], geo_t[0] + x_size * geo_t[1])
    ymin = min(geo_t[3], geo_t[3] + y_size * geo_t[5])
    ymax = max(geo_t[3], geo_t[3] + y_size * geo_t[5])
    return xmin, xmax, ymin, ymax


def convert_one_band_raster_to_mappable(path_raster):
    """Convert tiff to numpy matrix with bounding box.

    Args:
        path_raster (str): path to tiff file.

    Returns:
        dataset, xmin, xmax, ymin, ymax (tuple): numpy matrix
        and bounding box of the tiff file.
    """
    # Open raster file
    ds = gdal.Open(path_raster)
    if ds is None:
        print("Could not open")

    # Get coordinates, cols and rows
    cols = ds.RasterXSize
    rows = ds.RasterYSize

    xmin, xmax, ymin, ymax = get_extent(ds)

    # Raster convert to array in numpy
    bands = ds.RasterCount
    band = ds.GetRasterBand(1)
    dataset = expit(band.ReadAsArray(0, 0, cols, rows))

    return dataset, xmin, xmax, ymin, ymax


def import_commune_yields(data_files_list, path_to_population_image):
    """Imports yields from communes.

    Args:
        data_files_list (list of str): list of file to check.
        path_to_population_image (str): path to tif population files

    Returns:
        commune_to_yield_avg_by_year_by_crop, commune_dict (tuple): DataFrame
        and dictionnary to merge with main DataFrame.
    """
    commune_to_yield_avg_by_year_by_crop = {
        "2010": {},
        "2011": {},
        "2012": {},
        "2013": {},
        "2014": {},
    }
    commune_dict, commune_id, geometry = open_communes()
    crops = {}
    year = "2009"

    for data_file_index in range(len(data_files_list)):

        print(round(data_file_index / len(data_files_list) * 100), " %")

        data_file_name = data_files_list[data_file_index]

        if year != data_file_name.split("/")[-4]:
            year = data_file_name.split("/")[-4]
            (
                dataset_pop,
                xmin_pop,
                xmax_pop,
                ymin_pop,
                ymax_pop,
            ) = convert_one_band_raster_to_mappable(
                path_to_population_image + "/" + year + "_population.tif"
            )

        dataset, xmin, xmax, ymin, ymax = convert_one_band_raster_to_mappable(
            data_file_name
        )
        affine = rasterio.transform.from_bounds(
            xmin, ymin, xmax, ymax, dataset.shape[0], dataset.shape[1]
        )
        affine_pop = rasterio.transform.from_bounds(
            xmin_pop,
            ymin_pop,
            xmax_pop,
            ymax_pop,
            dataset_pop.shape[0],
            dataset_pop.shape[1],
        )

        for id in range(len(geometry)):

            mask = rasterize(
                shapes=[geometry[id]], out_shape=dataset.shape, transform=affine
            )
            mask_pop = rasterize(
                shapes=[geometry[id]], out_shape=dataset_pop.shape, transform=affine_pop
            )

            mask_sum = np.sum(mask)
            if mask_sum > 0:
                mean = np.sum(dataset * mask) / mask_sum / np.sum(mask_pop)
            else:
                mean = 0

            if (
                not commune_id[id]
                in commune_to_yield_avg_by_year_by_crop[
                    data_file_name.split("/")[-4]
                ].keys()
            ):
                commune_to_yield_avg_by_year_by_crop[data_file_name.split("/")[-4]][
                    commune_id[id]
                ] = {data_file_name.split("/")[-2]: mean}
            else:
                if (
                    not data_file_name.split("/")[-2]
                    in commune_to_yield_avg_by_year_by_crop[
                        data_file_name.split("/")[-4]
                    ][commune_id[id]].keys()
                ):
                    commune_to_yield_avg_by_year_by_crop[data_file_name.split("/")[-4]][
                        commune_id[id]
                    ][data_file_name.split("/")[-2]] = mean
                else:
                    commune_to_yield_avg_by_year_by_crop[data_file_name.split("/")[-4]][
                        commune_id[id]
                    ][data_file_name.split("/")[-2]] = max(
                        mean,
                        commune_to_yield_avg_by_year_by_crop[
                            data_file_name.split("/")[-4]
                        ][commune_id[id]][data_file_name.split("/")[-2]],
                    )
    return commune_to_yield_avg_by_year_by_crop, commune_dict


def join_yields(
    df_aggregated_match_for_FSMS_files,
    commune_to_yield_avg_by_year_by_crop,
    commune_dict,
):
    """Join yields to main DataFrame.

    Args:
        df_aggregated_match_for_FSMS_files (pd.DataFrame): main DataFrame
        commune_to_yield_avg_by_year_by_crop (pd.DataFrame): yields DataFrame
        commune_dict (dict): commune dictionnary

    Returns:
        df_aggregated_match_for_FSMS_files (pd.DataFrame): main DataFrame with yields.
    """
    new_columns = {
        "groundnut": [],
        "millet": [],
        "sorghum": [],
        "maize": [],
        "cowpea": [],
    }
    df_aggregated_match_for_FSMS_files = df_aggregated_match_for_FSMS_files.reset_index(drop=True)
   
    for row in df_aggregated_match_for_FSMS_files.index:
        
        if str(df_aggregated_match_for_FSMS_files.loc[row, "moughataa"]) != "nan":
            
            year = str(int(df_aggregated_match_for_FSMS_files.loc[row, "year"]) - 1)
            
            if ".0" in str(df_aggregated_match_for_FSMS_files.loc[row, "moughataa"]):
                
                village = str(df_aggregated_match_for_FSMS_files.loc[row, "moughataa"])[
                    :-2
                ]
                yields = commune_to_yield_avg_by_year_by_crop[year][village]
                for culture in new_columns.keys():
                    if culture in yields.keys():
                        new_columns[culture].append(yields[culture])
                    else:
                        new_columns[culture].append("")
            elif (
                df_aggregated_match_for_FSMS_files.loc[row, "moughataa"]
                in commune_dict.keys()
            ):
                village = commune_dict[
                    df_aggregated_match_for_FSMS_files.loc[row, "moughataa"]
                ]
                yields = commune_to_yield_avg_by_year_by_crop[year][village]
                for culture in new_columns.keys():
                    if culture in yields.keys():
                        new_columns[culture].append(yields[culture])
                    else:
                        new_columns[culture].append("")
            else:
                for culture in new_columns.keys():
                    new_columns[culture].append("")
        else:
            for culture in new_columns.keys():
                new_columns[culture].append("")

    for culture in new_columns.keys():
        df_aggregated_match_for_FSMS_files[culture] = new_columns[culture]
    return df_aggregated_match_for_FSMS_files
