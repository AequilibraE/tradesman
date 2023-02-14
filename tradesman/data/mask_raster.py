import rasterio.mask
import rasterio
import geopandas as gpd
from shapely.geometry import box


def mask_raster(dest_path, main_area):
    """
    This function was presented in: https://rasterio.readthedocs.io/en/latest/topics/masking-by-shapefile.html
    """
    with rasterio.open(dest_path) as src:
        out_img, out_transform = rasterio.mask.mask(src, areaGeoJson(main_area), crop=True)
        out_meta = src.meta

    out_meta.update(
        {"driver": "GTiff", "height": out_img.shape[1], "width": out_img.shape[2], "transform": out_transform}
    )

    with rasterio.open(dest_path, "w", **out_meta) as dest:
        dest.write(out_img)

    return rasterio.open(dest_path)


def areaGeoJson(main_area):
    """
    Adapted from the function and code created by Henrikki Tenkanen.
    See: https://automating-gis-processes.github.io/CSC18/lessons/L6/clipping-raster.html
    """
    import json

    geo = gpd.GeoDataFrame({"geometry": box(*main_area.bounds)}, index=[0], crs=4326)
    return [json.loads(geo.to_json())["features"][0]["geometry"]]
