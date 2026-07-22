from dataclasses import dataclass

@dataclass
class EnvironmentalAssessment:

    forecast_rainfall_mm: float

    observed_rainfall_mm: float | None

    rainfall_difference_mm: float | None

    accumulation_24h_mm: float | None

    accumulation_48h_mm: float | None

    accumulation_72h_mm: float | None

    maximum_interval_mm: float | None

    precipitation_trend: str | None

    weather_condition: str

    temperature_c: float

    sentinel_acquisition_date: str | None

    ndwi: float | None
    
    surface_water_area_m2: float | None
    
    mean_elevation_m: float | None
    
    minimum_elevation_m: float | None
    
    maximum_elevation_m: float | None
    
    mean_slope_percent: float | None



def build_environmental_assessment(

    forecast,

    gpm=None,

    sentinel=None,

    terrain=None,

):

    observed = None

    difference = None
    
    acc24 = None
    acc48 = None
    acc72 = None
    
    maximum = None

    trend = None
    
    if gpm:
    
        observed = gpm.latest_mm
    
        acc24 = gpm.accumulation_24h
    
        acc48 = gpm.accumulation_48h
    
        acc72 = gpm.accumulation_72h

        maximum = gpm.maximum_interval_mm
    
        trend = gpm.trend
    
    if observed is not None:
        
        difference = round(
    
            observed
            - forecast.rainfall,
    
            2,
    
        )

    return EnvironmentalAssessment(
    
        forecast_rainfall_mm=forecast.rainfall,

        observed_rainfall_mm=observed,
    
        rainfall_difference_mm=difference,
    
        accumulation_24h_mm=acc24,

        accumulation_48h_mm=acc48,
    
        accumulation_72h_mm=acc72,
    
        maximum_interval_mm=maximum,
    
        precipitation_trend=trend,
    
        weather_condition=forecast.weather_condition,
    
        temperature_c=forecast.temperature,

        sentinel_acquisition_date=(
            sentinel.acquisition_date
            if sentinel
            else None
        ),
    
        ndwi=(
            sentinel.ndwi
            if sentinel
            else None
        ),
    
        surface_water_area_m2=(
            sentinel.surface_water_area_m2
            if sentinel
            else None
        ),
    
        mean_elevation_m=(
            terrain.mean_elevation_m
            if terrain
            else None
        ),
        
        minimum_elevation_m=(
            terrain.minimum_elevation_m
            if terrain
            else None
        ),
        
        maximum_elevation_m=(
            terrain.maximum_elevation_m
            if terrain
            else None
        ),
        
        mean_slope_percent=(
            terrain.mean_slope_percent
            if terrain
            else None
        ),
    )