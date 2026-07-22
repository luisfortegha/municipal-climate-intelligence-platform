from dataclasses import dataclass


@dataclass
class FloodAssessment:

    rainfall_condition: str

    surface_water_condition: str

    terrain_condition: str

    flood_zone_condition: str

    overall_condition: str

    supporting_reasons: list[str]


def compute_flood_assessment(

    environmental,

    hazard,

    exposure,

):

    reasons = []

    rainfall = environmental.get(
        "accumulation_24h_mm"
    )

    ndwi = environmental.get(
        "ndwi"
    )

    slope = environmental.get(
        "mean_slope_percent"
    )

    surface_water = environmental.get(
        "surface_water_area_m2"
    )
    
    elevation = environmental.get(
        "mean_elevation_m"
    )

    affected = exposure.get(
        "affected_assets",
        0,
    )

    polygons = hazard.get(
        "polygon_count",
        0,
    )

    rainfall_condition = "Normal"

    if rainfall is not None:

        if rainfall >= 75:

            rainfall_condition = "Very High"

        elif rainfall >= 40:

            rainfall_condition = "High"

        elif rainfall >= 20:

            rainfall_condition = "Moderate"

    surface_condition = "Unknown"

    if ndwi is not None:

        if ndwi >= 0.4:

            surface_condition = "Extensive Water"

        elif ndwi >= 0.2:

            surface_condition = "Moderate Water"

        else:

            surface_condition = "Limited Water"

    terrain_condition = "Unknown"

    if slope is not None and elevation is not None:
    
        if slope <= 3 and elevation <= 150:
    
            terrain_condition = "Low Relief"
    
        elif slope <= 10:
    
            terrain_condition = "Rolling"
    
        else:
    
            terrain_condition = "Steep"
    
    elif slope is not None:
    
        if slope <= 3:
    
            terrain_condition = "Low Relief"
    
        elif slope <= 10:
    
            terrain_condition = "Rolling"
    
        else:

            terrain_condition = "Steep"
    
    flood_condition = "No Hazard"
    
    if polygons > 0:

        flood_condition = "Mapped Flood Hazard"

    if rainfall_condition in ["High", "Very High"]:

        reasons.append(
            "High accumulated rainfall."
        )

    if surface_condition == "Extensive Water":

        reasons.append(
            "Large detected surface water."
        )

    if (
        surface_water is not None
        and surface_water >= 100000
    ):

        reasons.append(
            "Large mapped surface water extent."
        )

    if affected > 0:

        reasons.append(
            "Infrastructure exposure identified."
        )

    if flood_condition == "Mapped Flood Hazard":

        reasons.append(
            "Mapped FEMA flood hazards present."
        )

    if terrain_condition == "Low Relief":

        reasons.append(
            "Low-relief terrain identified."
        )

    overall = "Routine Monitoring"

    if len(reasons) >= 3:

        overall = "Elevated Environmental Conditions"

    elif len(reasons) >= 1:

        overall = "Environmental Attention"

    return FloodAssessment(

        rainfall_condition=rainfall_condition,

        surface_water_condition=surface_condition,

        terrain_condition=terrain_condition,

        flood_zone_condition=flood_condition,

        overall_condition=overall,

        supporting_reasons=reasons,

    )