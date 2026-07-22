from dataclasses import dataclass
from typing import Optional

import geopandas as gpd

from analysis.providers.jrc import JRCProvider


@dataclass
class HazardEvidence:

    historical_water_occurrence: float

    seasonality: float

    water_area_fraction: float

    geometry: gpd.GeoDataFrame


def assess_hazard(study_area):

    provider = JRCProvider()

    return provider.load(study_area)