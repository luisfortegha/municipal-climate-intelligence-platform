from dataclasses import dataclass

from earth_observation.gpm import GPMObservation


@dataclass
class EnvironmentalAssessment:

    forecast_rainfall_mm: float

    observed_rainfall_mm: float | None

    rainfall_difference_mm: float | None

    ndwi: float | None

    surface_water_area_m2: float | None

    average_elevation_m: float | None

    average_slope_percent: float | None


def build_environmental_assessment(
    forecast,
    gpm: GPMObservation | None = None,
    sentinel: SentinelObservation | None = None,
    dem: TerrainObservation | None = None,
):

    observed = None

    if gpm:

        observed = gpm.observed_precipitation_mm

    rainfall_difference = None

    if observed is not None:

        rainfall_difference = (
            observed
            - forecast.rainfall
        )

    ndwi = None

    surface_water = None

    if sentinel:

        ndwi = sentinel.ndwi

        surface_water = (
            sentinel.surface_water_area_m2
        )

    return EnvironmentalAssessment(

        forecast_rainfall_mm=forecast.rainfall,

        observed_rainfall_mm=observed,

        rainfall_difference_mm=rainfall_difference,

        ndwi=ndwi,

        surface_water_area_m2=surface_water,

        average_elevation_m=(
            dem.mean_elevation_m
            if dem
            else None
        ),

        average_slope_percent=(
            dem.mean_slope_percent
            if dem
            else None
        ),
    )