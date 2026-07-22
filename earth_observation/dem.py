from dataclasses import dataclass

from earth_observation.stac import CATALOG

import numpy as np
import os
import pickle
import time
import planetary_computer
from odc.stac import load


class DEMServiceError(Exception):
    """Raised when DEM data cannot be retrieved."""
    pass


@dataclass
class TerrainObservation:

    mean_elevation_m: float | None

    minimum_elevation_m: float | None

    maximum_elevation_m: float | None

    mean_slope_percent: float | None

    source: str

    status: str

def get_latest_observation(
    study_area,
) -> TerrainObservation:

    west, south, east, north = study_area.bounds

    cache_dir = "cache"

    os.makedirs(
        cache_dir,
        exist_ok=True,
    )

    cache_file = os.path.join(
        cache_dir,
        f"dem_{study_area.name}.pkl",
    )

    CACHE_DAYS = 30

    if os.path.exists(cache_file):
    
        age_seconds = (
            time.time()
            - os.path.getmtime(cache_file)
        )

        if age_seconds < CACHE_DAYS * 86400:
    
            with open(cache_file, "rb") as f:

                return pickle.load(f)

    search = CATALOG.search(

        collections=[
            "cop-dem-glo-30"
        ],

        bbox=(
            west,
            south,
            east,
            north,
        ),

        limit=1,

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
                f"DEM STAC search failed "
                f"(attempt {attempt+1}/3)"
            )
    
            time.sleep(
                2 ** attempt
            )
    
    if items is None:
    
        return TerrainObservation(
    
            mean_elevation_m=None,
    
            minimum_elevation_m=None,
    
            maximum_elevation_m=None,
    
            mean_slope_percent=None,
    
            source="Copernicus DEM",
    
            status="Service Unavailable",
        )
    
    if not items:

        return TerrainObservation(

            mean_elevation_m=None,

            minimum_elevation_m=None,

            maximum_elevation_m=None,

            mean_slope_percent=None,

            source="Copernicus DEM",

            status="No DEM",
        )

    item = planetary_computer.sign(
        items[0]
    )
    
    items = [item]

    dataset = load(
        [item],
        bands=["data"],
        geopolygon=study_area.polygon,
        resolution=30,
        chunks=None,
    )
    
    elevation = (
        dataset["data"]
        .astype("float32")
        .values
        .squeeze()
    )

    print("Elevation shape:", elevation.shape)
    print("Total pixels:", elevation.size)
    print("All NaN:", np.all(np.isnan(elevation)))
    
    if not np.all(np.isnan(elevation)):
        print("Minimum:", np.nanmin(elevation))
        print("Maximum:", np.nanmax(elevation))
    
    if elevation.size == 0 or np.all(np.isnan(elevation)):

        raise DEMServiceError(
            "DEM contains no valid elevation values."
        )

    mean_elevation = float(
        np.nanmean(
            elevation
        )
    )
    
    minimum = float(
        np.nanmin(
            elevation
        )
    )
    
    maximum = float(
        np.nanmax(
            elevation
        )
    )

    pixel_size = 30.0

    gy, gx = np.gradient(
        elevation,
        pixel_size,
        pixel_size,
    )
    
    slope_percent = np.sqrt(
        gx**2 + gy**2,
    ) * 100.0
    
    mean_slope = float(
        np.nanmean(
            slope_percent
        )
    )

    observation = TerrainObservation(

        mean_elevation_m=mean_elevation,
    
        minimum_elevation_m=minimum,
    
        maximum_elevation_m=maximum,
    
        mean_slope_percent=mean_slope,
    
        source="Copernicus DEM",
    
        status="Operational",
    )

    with open(cache_file, "wb") as f:
    
        pickle.dump(
            observation,
            f,
        )

    return observation