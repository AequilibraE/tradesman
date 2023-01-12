import rasterio.mask
import rasterio


def mask_raster(dest_path, main_area):
    with rasterio.open(dest_path) as src:
        out_img, out_transform = rasterio.mask.mask(src, main_area, crop=True)
        out_meta = src.meta

    out_meta.update({"driver": "GTiff",
                     "height": out_img.shape[1],
                     "width": out_img.shape[2],
                     "transform": out_transform})

    with rasterio.open(dest_path, "w", **out_meta) as dest:
        dest.write(out_img)

    return rasterio.open(dest_path)
