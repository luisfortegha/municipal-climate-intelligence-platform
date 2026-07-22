from dataclasses import dataclass

import geopandas as gpd


@dataclass
class HazardMetrics:

    total_hazard_area_km2: float

    largest_hazard_polygon_km2: float

    municipality_area_km2: float

    percent_area_affected: float

    unique_fema_zones: int

    dominant_fema_zone: str


def compute_hazard_metrics(
    study_area,
    hazard_gdf: gpd.GeoDataFrame,
) -> HazardMetrics:

    if hazard_gdf is None or hazard_gdf.empty:

        return HazardMetrics(
            total_hazard_area_km2=0,
            largest_hazard_polygon_km2=0,
            municipality_area_km2=0,
            percent_area_affected=0,
            unique_fema_zones=0,
            dominant_fema_zone="--",
        )

    projected = "EPSG:3857"

    municipality = gpd.GeoDataFrame(
        geometry=[study_area.polygon],
        crs="EPSG:4326",
    ).to_crs(projected)

    hazards = hazard_gdf.to_crs(projected)

    municipality_area = municipality.area.iloc[0]

    total_hazard_area = hazards.area.sum()

    largest_polygon = hazards.area.max()

    percent = (
        total_hazard_area
        / municipality_area
        * 100
    )

    zones = (
        hazard_gdf["FloodZone"]
        .fillna("Unknown")
        .astype(str)
    )

    dominant = zones.mode().iloc[0]

    return HazardMetrics(

        total_hazard_area_km2=round(
            total_hazard_area / 1_000_000,
            2,
        ),

        largest_hazard_polygon_km2=round(
            largest_polygon / 1_000_000,
            2,
        ),

        municipality_area_km2=round(
            municipality_area / 1_000_000,
            2,
        ),

        percent_area_affected=round(
            percent,
            2,
        ),

        unique_fema_zones=zones.nunique(),

        dominant_fema_zone=dominant,
    )