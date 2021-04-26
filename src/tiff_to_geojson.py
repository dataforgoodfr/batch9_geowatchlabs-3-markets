import os
import rasterio
from rasterio.features import shapes
import geopandas as gpd


def convert_tiff_to_geojson(original_tiff_path, destination_geojson_path, band):
    """
        Convert tiff file to geojson for GeoDataFrame handling.

    Args:
        original_tiff_path (str): path+name of the tiff file we want to convert
        destination_geojson_path (str): path+name of the targeted geojson
        band (int): tiff band you want to handle

    Returns:
        Upload the geojson file in the destination.
    """
    data = rasterio.open(original_tiff_path).meta
    c = str(data["crs"])

    mask = None
    with rasterio.open(original_tiff_path) as src:
        image = src.read(band)  # first band
        results = (
            {"properties": {"property": v}, "geometry": s}
            for i, (s, v) in enumerate(
                shapes(image, mask=mask, transform=data["transform"])
            )
        )

    geoms = list(results)
    gpd_polygonized_raster = gpd.GeoDataFrame.from_features(geoms, crs=c)
    gpd_polygonized_raster.to_file(destination_geojson_path, driver="GeoJSON")


if __name__ == "__main__":
    tiff_1 = "asset/2015_birth.tiff"
    tiff_2 = "asset/2015_population.tiff"
    tiff_3 = "asset/subset_S3B_OL_2_LFR____20210421T103548_20210421T103848_20210422T155447_0179_051_279_2520_LN1_O_NT_002.tiff"
    geojson_1 = "asset/2015_birth.geojson"
    geojson_2 = "asset/2015_population.geojson"
    geojson_3 = "asset/subset_S3B_OL_2_LFR____20210421T103548_20210421T103848_20210422T155447_0179_051_279_2520_LN1_O_NT_002.geojson"
    for file in os.listdir("asset/tiff"):
        print("Conversion of "+file+" starting ...")
        try:
            if file.replace("tiff","geojson") not in os.listdir("asset/geojson"):
                tiff_path = os.getcwd()+"asset/tiff/"+file
                geojson_path = tiff_path.replace("tiff","geojson")
                convert_tiff_to_geojson(tiff_path, geojson_path, 1)
                print("Conversion of "+file+" successful !")
        except Exception as e:
            print("Couldn't convert file "+file+", exception :"+e.__str__())