from pathlib import Path

import numpy as np
import rasterio
from rasterio.mask import mask


def open_raster(path):
    """
    Opens a raster dataset.
    """
    return rasterio.open(Path(path))


def read_window(src, bounds):
    """
    Reads a bounding box from an opened raster.

    Parameters
    ----------
    src : rasterio DatasetReader

    bounds : (minx, miny, maxx, maxy)
    """

    from rasterio.windows import from_bounds

    minx, miny, maxx, maxy = bounds

    window = from_bounds(
        minx,
        miny,
        maxx,
        maxy,
        src.transform,
    )

    data = src.read(
        1,
        window=window,
        masked=True,
    )

    transform = src.window_transform(window)

    return data, transform


def clip_to_polygon(src, polygon):
    """
    Clips a raster to a shapely polygon.
    """

    data, transform = mask(
        src,
        [polygon],
        crop=True,
    )

    return data[0], transform


def compute_statistics(data):
    """
    Computes simple raster statistics.
    """

    valid = data.compressed()

    if len(valid) == 0:

        return {
            "mean": 0.0,
            "maximum": 0.0,
            "minimum": 0.0,
            "pixels": 0,
        }

    return {
        "mean": float(np.mean(valid)),
        "maximum": float(np.max(valid)),
        "minimum": float(np.min(valid)),
        "pixels": int(valid.size),
    }