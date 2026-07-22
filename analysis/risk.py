from dataclasses import dataclass
from typing import Dict
from analysis.environmental_assessment import EnvironmentalAssessment

@dataclass
class EngineeringAssessment:

    forecast_rainfall_mm: float

    observed_rainfall_mm: float | None

    rainfall_difference_mm: float | None

    accumulation_24h_mm: float | None

    accumulation_48h_mm: float | None

    accumulation_72h_mm: float | None

    maximum_interval_mm: float | None

    precipitation_trend: str | None

    ndwi: float | None

    surface_water_area_m2: float | None

    sentinel_acquisition_date: str | None

    mean_elevation_m: float | None

    minimum_elevation_m: float | None

    maximum_elevation_m: float | None
    
    mean_slope_percent: float | None

    weather_alerts: int

    hazard_polygons: int

    affected_assets: int

    hospitals: int

    schools: int

    fire_stations: int

    police: int

    roads: int

    assessment_basis: str

    exposed_critical_facilities: int

    exposure_ratio: float


def compute_engineering_assessment(
    environment: EnvironmentalAssessment,
    findings: Dict,
) -> EngineeringAssessment:

    summary = findings.get(
        "summary",
        {},
    )

    exposure = findings.get(
        "exposure_assessment",
        {},
    )
    
    critical = (
        summary.get("hospitals", 0)
        + summary.get("fire_stations", 0)
        + summary.get("police", 0)
    )
    
    assets = summary.get(
        "total_assets",
        0,
    )
    
    ratio = 0.0
    
    if assets > 0:
    
        ratio = round(
            critical / assets,
            2,
        )
    
    return EngineeringAssessment(

        forecast_rainfall_mm=environment.forecast_rainfall_mm,
    
        observed_rainfall_mm=environment.observed_rainfall_mm,
    
        rainfall_difference_mm=environment.rainfall_difference_mm,
    
        accumulation_24h_mm=environment.accumulation_24h_mm,
    
        accumulation_48h_mm=environment.accumulation_48h_mm,
    
        accumulation_72h_mm=environment.accumulation_72h_mm,
    
        maximum_interval_mm=environment.maximum_interval_mm,
    
        precipitation_trend=environment.precipitation_trend,
    
        ndwi=environment.ndwi,
    
        surface_water_area_m2=environment.surface_water_area_m2,
    
        sentinel_acquisition_date=environment.sentinel_acquisition_date,
    
        mean_elevation_m=environment.mean_elevation_m,
    
        minimum_elevation_m=environment.minimum_elevation_m,
    
        maximum_elevation_m=environment.maximum_elevation_m,
    
        mean_slope_percent=environment.mean_slope_percent,
    
        weather_alerts=0,
    
        hazard_polygons=0,
    
        affected_assets=summary.get(
            "total_assets",
            0,
        ),
    
        hospitals=summary.get(
            "hospitals",
            0,
        ),
    
        schools=summary.get(
            "schools",
            0,
        ),
    
        fire_stations=summary.get(
            "fire_stations",
            0,
        ),
    
        police=summary.get(
            "police",
            0,
        ),
    
        roads=summary.get(
            "roads",
            0,
        ),
    
        assessment_basis ="Environmental Assessment",
    
        exposed_critical_facilities=(
            summary.get("hospitals", 0)
            + summary.get("fire_stations", 0)
            + summary.get("police", 0)
        ),
    
        exposure_ratio=round(
            summary.get("total_assets", 0)
            /
            max(
                1,
                exposure.get(
                    "total_assets",
                    1,
                ),
            ),
            2,
        ),
    )        