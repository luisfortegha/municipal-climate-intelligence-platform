from dataclasses import dataclass
import geopandas as gpd
from shapely.geometry import shape
from rasterio.features import shapes
from affine import Affine
import numpy as np
import os
import pickle
import time
import planetary_computer
from odc.stac import load
import pystac_client
import time
from pystac_client.exceptions import APIError
from earth_observation.stac import CATALOG

class SentinelServiceError(Exception):
    """Raised when Sentinel-2 imagery cannot be retrieved."""
    pass


@dataclass
class SentinelObservation:

    acquisition_date: str | None

    ndwi: float | None

    surface_water_area_m2: float | None

    surface_water_gdf: gpd.GeoDataFrame | None

    cloud_cover_percent: float | None

    source: str

    status: str


def get_latest_observation(
    study_area,
) -> SentinelObservation:
    west, south, east, north = study_area.bounds

    cache_dir = "cache"

    os.makedirs(
        cache_dir,
        exist_ok=True,
    )
    
    west, south, east, north = study_area.bounds

    cache_file = os.path.join(
        cache_dir,
        (
            "sentinel_"
            f"{west:.4f}_"
            f"{south:.4f}_"
            f"{east:.4f}_"
            f"{north:.4f}.pkl"
        ),
    )

    CACHE_DAYS = 7

    if os.path.exists(cache_file):

        age_seconds = (
            time.time()
            - os.path.getmtime(cache_file)
        )

        if age_seconds < CACHE_DAYS * 86400:

            with open(cache_file, "rb") as f:
    
                return pickle.load(f)

    search = CATALOG.search(
        collections=["sentinel-2-l2a"],
        bbox=(west, south, east, north),
        datetime="2024-01-01/..",
        query={
            "eo:cloud_cover": {
                "lt": 20
            }
        },
        sortby=[
            {
                "field": "properties.datetime",
                "direction": "desc",
            }
        ],
        limit=5,
    )
    
    items = None
    last_error = None
    
    for attempt in range(3):
    
        try:
    
            items = list(search.items())
    
            break
    
        except APIError as ex:
    
            last_error = ex
    
            print(
                f"Sentinel STAC search failed "
                f"(attempt {attempt + 1}/3)"
            )
    
            time.sleep(
                2 ** attempt
            )
    
    if items is None:
    
        raise SentinelServiceError(
            f"Planetary Computer search failed: {last_error}"
        )
    
    if not items:
    
        return SentinelObservation(

            acquisition_date=None,
    
            ndwi=None,
    
            surface_water_area_m2=None,

            surface_water_gdf=None,
    
            cloud_cover_percent=None,
    
            source="Sentinel-2",
    
            status="No imagery found",
        )
        
    last_exception = None
    
    for raw_item in items:
    
        try:
    
            item = planetary_computer.sign(raw_item)
    
            items = [item]
    
            break
    
        except Exception as ex:
    
            last_exception = ex
    
    else:
    
        return SentinelObservation(

            acquisition_date=None,
        
            ndwi=None,
        
            surface_water_area_m2=None,
        
            cloud_cover_percent=None,
        
            source="Sentinel-2",
        
            status="Service Unavailable",
        )

    bbox = (
        west,
        south,
        east,
        north,
    )

    dataset = load(
        items,
        bands=["green", "nir"],
        bbox=bbox,
        resolution=10,
        chunks=None,
    )

    green = (
        dataset["green"]
        .astype("float32")
        .load()
        .values
    )
    
    nir = (
        dataset["nir"]
        .astype("float32")
        .load()
        .values
    )
        
    denominator = green + nir

    ndwi = np.where(
        denominator != 0,
        (green - nir) / denominator,
        np.nan,
    )

    ndwi = np.squeeze(ndwi)

    ndwi = np.squeeze(ndwi)

    valid = np.isfinite(ndwi)

    ndwi_valid = ndwi[valid]

    if ndwi_valid.size == 0:
        raise RuntimeError("No valid Sentinel pixels found.")

    mean_ndwi = float(np.nanmean(ndwi))

    water = ndwi > 0.30

    # ---------------------------------------
    # Convert water mask to polygons
    # ---------------------------------------

    transform = dataset.geobox.affine

    features = []
    
    for geom, value in shapes(
        water.astype("uint8"),
        mask=water,
        transform=transform,
    ):

        if value == 1:

            features.append(
                shape(geom)
            )

    if features:

        surface_water_gdf = gpd.GeoDataFrame(
            geometry=features,
            crs="EPSG:4326",
        )

    else:

        surface_water_gdf = gpd.GeoDataFrame(
            geometry=[],
            crs="EPSG:4326",
        )

    water_pixels = np.count_nonzero(water)

    surface_water_area_m2 = water_pixels * 100.0

    observation = SentinelObservation(

        acquisition_date=item.datetime.date().isoformat()
        if item.datetime
        else None,
    
        ndwi=mean_ndwi,
    
        surface_water_area_m2=surface_water_area_m2,
    
        surface_water_gdf=surface_water_gdf,
    
        cloud_cover_percent=item.properties.get(
            "eo:cloud_cover"
        ),

        source="Sentinel-2",
    
        status="OK",
    )

    with open(cache_file, "wb") as f:
    
        pickle.dump(
            observation,
            f,
        )

    return observation