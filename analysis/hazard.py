from dataclasses import dataclass
from typing import Any, List

import geopandas as gpd

from analysis.logger import logger


class HazardServiceError(Exception):
    """Raised when hazard processing fails."""
    pass


@dataclass
class HazardZone:
    zone_id: str
    area_name: str
    hazard_class: str
    geometry: Any


@dataclass
class HazardAssessment:
    intersects: bool
    zones: List[HazardZone]


def assess_hazard(
    study_area,
    hazard_geojson_path=None,
):
    """
    Global hazard placeholder.

    The engineering assessment relies on:
    - NASA GPM
    - Sentinel-2
    - Copernicus DEM
    - Infrastructure
    - Hydrology

    A dedicated global hazard provider will be added
    in a future release.
    """

    logger.info("Running global hazard assessment.")

    return (
        HazardAssessment(
            intersects=False,
            zones=[],
        ),
        gpd.GeoDataFrame(
            geometry=[],
            crs="EPSG:4326",
        ),
    )