import osmnx as ox
import pandas as pd
import streamlit as st
import geopandas as gpd
import math
import pickle
import time
from pathlib import Path
from typing import Dict, Any, List
from analysis.environmental_assessment import EnvironmentalAssessment
from analysis.hazard import HazardAssessment
from analysis.risk import compute_engineering_assessment
from analysis.logger import logger
from osmnx._errors import InsufficientResponseError

ox.settings.use_cache = True
ox.settings.log_console = False

CACHE_DIR = Path("cache")

CACHE_DIR.mkdir(
    exist_ok=True,
)

CACHE_HOURS = 24

class InfrastructureRetrievalError(Exception):
    """Raised when infrastructure data cannot be retrieved from OSM."""
    pass

def safe_fetch(fetch_fn, bbox, tags):
    """Run an OSM query and return an empty GeoDataFrame if no features exist."""
    try:
        return fetch_fn(
            bbox=bbox,
            tags=tags,
        )
    except InsufficientResponseError:
        return gpd.GeoDataFrame(
            geometry=[],
            crs="EPSG:4326",
        )

def retrieve_infrastructure(
    study_area,
    hazard_gdf=None,
) -> Dict[str, gpd.GeoDataFrame]:
    """
    Retrieves critical infrastructure assets (schools, hospitals, fire stations, and primary roads)
    within a buffer distance (in meters) around a specified latitude/longitude point using OSMnx.
    
    Returns a dictionary containing GeoDataFrames for each asset class:
    - 'schools'
    - 'hospitals'
    - 'fire_stations'
    - 'primary_roads'
    """
    fetch_fn = (
        getattr(ox, "features_from_bbox", None)
        or getattr(ox, "geometries_from_bbox", None)
    )

    if (
        hazard_gdf is not None
        and not hazard_gdf.empty
    ):

        west, south, east, north = hazard_gdf.total_bounds

        margin = 0.003

        west -= margin
        south -= margin
        east += margin
        north += margin

    else:

        west, south, east, north = study_area.bounds

        # Approximate study-area size in km²
        mean_lat = (south + north) / 2

        height_km = (north - south) * 111.32

        width_km = (
            (east - west)
            * 111.32
            * math.cos(math.radians(mean_lat))
        )

        area_km2 = abs(width_km * height_km)

        logger.info(
            "Custom study area: %.2f km²",
            area_km2,
        )

        if area_km2 > 3000:
            raise InfrastructureRetrievalError(
                f"Study area is too large ({area_km2:.1f} km²). "
                "Please draw a smaller rectangle."
            )

    if study_area.name not in (
        "Interactive Study Area",
        "Custom Study Area",
        "Draw Study Area",
    ):

        cache_name = study_area.name.replace(" ", "_")

    else:

        west, south, east, north = study_area.bounds

        cache_name = (
            f"{west:.4f}_"
            f"{south:.4f}_"
            f"{east:.4f}_"
            f"{north:.4f}"
        )

    cache_file = CACHE_DIR / f"osm_{cache_name}.pkl"

    if cache_file.exists():

        age = (
            time.time()
            - cache_file.stat().st_mtime
        )

        if age < CACHE_HOURS * 3600:

            logger.info(
                "Using cached OSM infrastructure."
            )

            with open(
                cache_file,
                "rb",
            ) as f:

                return pickle.load(f)

    if fetch_fn is None:
        raise InfrastructureRetrievalError("OSMnx installation is missing features_from_point/geometries_from_point attribute.")

    results = {}

    # ------------------------------------------------------------------
    # Civic facilities (1 request)
    # ------------------------------------------------------------------

    civic = safe_fetch(
        fetch_fn,
        (west, south, east, north),
        {
            "amenity": [
                "school",
                "hospital",
                "fire_station",
                "police",
                "townhall",
            ]
        },
    )

    if not civic.empty:

        if civic.crs != "EPSG:4326":
            civic = civic.to_crs("EPSG:4326")

        civic = civic[
            civic.geometry.intersects(
                study_area.polygon
            )
        ].copy()

    results["schools"] = civic[civic["amenity"] == "school"].copy()
    results["hospitals"] = civic[civic["amenity"] == "hospital"].copy()
    results["fire_stations"] = civic[civic["amenity"] == "fire_station"].copy()
    results["police"] = civic[civic["amenity"] == "police"].copy()
    results["city_halls"] = civic[civic["amenity"] == "townhall"].copy()

    # ------------------------------------------------------------------
    # Emergency services (1 request)
    # ------------------------------------------------------------------

    results["emergency_services"] = gpd.GeoDataFrame(
        geometry=[],
        crs="EPSG:4326",
    )

    # ------------------------------------------------------------------
    # Roads (1 request)
    # ------------------------------------------------------------------

    results["primary_roads"] = safe_fetch(
        fetch_fn,
        (west, south, east, north),
        {
            "highway": [
                "primary",
                "secondary",
                "tertiary",
            ]
        },
    )

    if not results["primary_roads"].empty:

        if results["primary_roads"].crs != "EPSG:4326":
            results["primary_roads"] = (
                results["primary_roads"]
                .to_crs("EPSG:4326")
            )

        results["primary_roads"] = (
            results["primary_roads"][
                results["primary_roads"].geometry.intersects(
                    study_area.polygon
                )
            ].copy()
        )

    # ------------------------------------------------------------------
    # Water (1 request)
    # ------------------------------------------------------------------

    water = safe_fetch(
        fetch_fn,
        (west, south, east, north),
        {
            "waterway": True,
            "natural": "water",
        },
    )

    if not water.empty:

        if water.crs != "EPSG:4326":
            water = water.to_crs("EPSG:4326")

        water = water[
            water.geometry.intersects(
                study_area.polygon
            )
        ].copy()

    results["waterways"] = (
        water[water["waterway"].notna()].copy()
        if "waterway" in water.columns
        else water.iloc[0:0].copy()
    )

    results["water"] = (
        water[water["natural"] == "water"].copy()
        if "natural" in water.columns
        else water.iloc[0:0].copy()
    )

    # ------------------------------------------------------------------
    # Utilities (1 request)
    # ------------------------------------------------------------------

    utilities = safe_fetch(
        fetch_fn,
        (west, south, east, north),
        {
            "office": "government",
            "man_made": [
                "water_works",
                "wastewater_plant",
            ],
            "power": "substation",
        },
    )

    if not utilities.empty:

        if utilities.crs != "EPSG:4326":
            utilities = utilities.to_crs("EPSG:4326")

        utilities = utilities[
            utilities.geometry.intersects(
                study_area.polygon
            )
        ].copy()

    # ------------------------------------------------------------------
    # Utilities classification (safe for missing OSM tags)
    # ------------------------------------------------------------------

    def empty_like(gdf):
        return gdf.iloc[0:0].copy()
    
    results["public_works"] = (
        utilities[utilities["office"] == "government"].copy()
        if "office" in utilities.columns
        else empty_like(utilities)
    )

    results["water_treatment"] = (
        utilities[utilities["man_made"] == "water_works"].copy()
        if "man_made" in utilities.columns
        else empty_like(utilities)
    )

    results["wastewater_treatment"] = (
        utilities[utilities["man_made"] == "wastewater_plant"].copy()
        if "man_made" in utilities.columns
        else empty_like(utilities)
    )

    results["power_substations"] = (
        utilities[utilities["power"] == "substation"].copy()
        if "power" in utilities.columns
        else empty_like(utilities)
    )

    # ------------------------------------------------------------------
    # Ensure every layer exists
    # ------------------------------------------------------------------

    for key in [
        "schools",
        "hospitals",
        "fire_stations",
        "police",
        "emergency_services",
        "primary_roads",
        "waterways",
        "water",
        "city_halls",
        "public_works",
        "water_treatment",
        "wastewater_treatment",
        "power_substations",
    ]:

        gdf = results.get(key)

        if gdf is None or gdf.empty:
            results[key] = gpd.GeoDataFrame(
                geometry=[],
                crs="EPSG:4326",
            )
    with open(
        cache_file,
        "wb",
    ) as f:
    
        pickle.dump(
            results,
            f,
        )

    return results

CACHE_DIR = Path("cache")

CACHE_DIR.mkdir(
    exist_ok=True,
)

def _is_nan(val) -> bool:
    """Helper to check if a value is NaN."""
    try:
        return math.isnan(val)
    except Exception:
        return False

def analyze_affected_infrastructure(
    environment: EnvironmentalAssessment,
    infra_gdfs: Dict[str, gpd.GeoDataFrame],
) -> Dict[str, Any]:
    """
    Performs deterministic GIS spatial analysis intersecting critical infrastructure GDFs 
    with active hazard zones in HazardAssessment.
    
    Returns a structured findings dictionary containing:
    - affected_infrastructure (list of assets)
    - supporting_evidence (dict of weather and hazard zone telemetry)
    """
    
    nearby_assets = []
    affected_assets = []

    projected_crs = "EPSG:3857"

    waterways = infra_gdfs.get("waterways")
    
    if waterways is None or waterways.empty:
    
        waterways_projected = None
    
    else:
    
        waterways_projected = waterways.to_crs(projected_crs)
    
        waterways_projected["geometry"] = (
            waterways_projected.buffer(150)
        )
    
    for category, assets in infra_gdfs.items():

        if assets.empty:
            continue

        assets = assets.copy()

        joined = assets.iloc[0:0].copy()

        if assets.geometry.is_empty.all():
            continue

        if assets.crs != projected_crs:
            assets = assets.to_crs(projected_crs)

        if waterways_projected is None:

            nearby100 = assets.iloc[0:0].copy()
            nearby250 = assets.iloc[0:0].copy()

        else:

            joined = gpd.sjoin(
                assets,
                waterways_projected,
                how="inner",
                predicate="intersects",
            )

            buffer100 = waterways_projected.copy()
            buffer100["geometry"] = buffer100.buffer(100)

            buffer250 = waterways_projected.copy()
            buffer250["geometry"] = buffer250.buffer(250)

            nearby100 = gpd.sjoin(
                assets,
                buffer100,
                how="inner",
                predicate="intersects",
            )

            nearby250 = gpd.sjoin(
                assets,
                buffer250,
                how="inner",
                predicate="intersects",
            )

        if joined.empty:
            continue

        filtered = []

        for _, row in joined.iterrows():

            review_score = 0
        
            rainfall72 = environment.accumulation_72h_mm or 0
        
            if rainfall72 >= 75:
                review_score += 3
        
            elif rainfall72 >= 50:
                review_score += 2
        
            elif rainfall72 >= 25:
                review_score += 1
        
            if environment.surface_water_area_m2:
        
                if environment.surface_water_area_m2 > 0:
                    review_score += 2
        
            if environment.mean_slope_percent is not None:
        
                if environment.mean_slope_percent <= 5:
                    review_score += 1

            if review_score >= 3:
        
                filtered.append(row)

        if filtered:
            joined = gpd.GeoDataFrame(
                filtered,
                geometry="geometry",
                crs=assets.crs,
            )
        else:
            joined = joined.iloc[0:0].copy()

        if joined.empty:
            continue

        for _, row in joined.iterrows():

            asset_id = str(
                row.get(
                    "osmid",
                    row.name,
                )
            )

            asset_name = row.get("name")

            if not asset_name or _is_nan(asset_name):

                asset_name = (
                    f"Unnamed {category.replace('_',' ').title()} ({asset_id})"
                )

            geom = row.geometry

            if geom is None:
                continue
            
            center = geom.representative_point()
            
            lat = center.y
            lon = center.x


            affected_assets.append(
                {
                    "id": asset_id,
                    "osm_id": asset_id,
                    "name": str(asset_name),
                    "type": category.replace("_", " ").title(),
                    "osm_layer": category,
                    "geometry": row.geometry,
                    "latitude": lat,
                    "longitude": lon,
                }
            )

        for _, row in nearby100.iterrows():

            nearby_assets.append(
                {
                    "id": str(row.get("osmid", row.name)),
                    "name": str(row.get("name", "Unnamed")),
                    "type": category.replace("_", " ").title(),
                    "distance_class": "Within 100 m",
                }
            )

        for _, row in nearby250.iterrows():

            nearby_assets.append(
                {
                    "id": str(row.get("osmid", row.name)),
                    "name": str(row.get("name", "Unnamed")),
                    "type": category.replace("_", " ").title(),
                    "distance_class": "Within 250 m",
                }
            )

    affected_assets = list(
        {
            (a["type"], a["id"]): a
            for a in affected_assets
        }.values()
    )

    from collections import defaultdict

    grouped = {}

    for asset in nearby_assets:

        key = (
            asset["name"],
            asset["type"],
        )

        if key not in grouped:

            grouped[key] = {
                "name": asset["name"],
                "type": asset["type"],
                "distance_class": asset["distance_class"],
                "segments": 1,
            }

        else:

            grouped[key]["segments"] += 1

            # Keep the closest distance
            if (
                grouped[key]["distance_class"]
                == "Within 250 m"
                and asset["distance_class"] == "Within 100 m"
            ):
                grouped[key]["distance_class"] = "Within 100 m"
    
    nearby_assets = list(grouped.values())

    # 2. Formulate supporting evidence
    supporting_evidence = {
        "weather": {
            "forecast_rainfall_mm": environment.forecast_rainfall_mm,
            "observed_rainfall_mm": environment.observed_rainfall_mm,
            "accumulation_24h_mm": environment.accumulation_24h_mm,
            "accumulation_48h_mm": environment.accumulation_48h_mm,
            "accumulation_72h_mm": environment.accumulation_72h_mm,
            "precipitation_trend": environment.precipitation_trend,
            "temperature_c": environment.temperature_c,
            "weather_condition": environment.weather_condition,
        },
        "environment": {
            "surface_water_area_m2": environment.surface_water_area_m2,
            "ndwi": environment.ndwi,
            "mean_slope_percent": environment.mean_slope_percent,
        },
    }

    summary = {
        "schools": 0,
        "hospitals": 0,
        "fire_stations": 0,
        "police": 0,
        "emergency_services": 0,
        "city_halls": 0,
        "public_works": 0,
        "water_treatment": 0,
        "wastewater_treatment": 0,
        "waterways": 0,
        "water": 0,
        "power_substations": 0,
        "roads": 0,
        "total_assets": len(affected_assets),
    }

    for asset in affected_assets:

        layer = asset["osm_layer"]

        if layer == "schools":
            summary["schools"] += 1

        elif layer == "hospitals":
            summary["hospitals"] += 1

        elif layer == "fire_stations":
            summary["fire_stations"] += 1

        elif layer == "police":
            summary["police"] += 1

        elif layer == "emergency_services":
            summary["emergency_services"] += 1

        elif layer == "primary_roads":
            summary["roads"] += 1

        elif layer == "city_halls":

            summary["city_halls"] += 1
        
        elif layer == "public_works":

            summary["public_works"] += 1

        elif layer == "water_treatment":
        
            summary["water_treatment"] += 1
        
        elif layer == "wastewater_treatment":
        
            summary["wastewater_treatment"] += 1
        
        elif layer == "waterways":
        
            summary["waterways"] += 1
        
        elif layer == "water":
        
            summary["water"] += 1

        elif layer == "power_substations":

            summary["power_substations"] += 1

    logger.info("===== Affected Infrastructure =====")

    for asset in affected_assets:
        logger.info(
            f"{asset['osm_layer']} | {asset['type']} | {asset['name']}"
        )
    
    logger.info(f"Summary: {summary}")

    engineering_assessment = compute_engineering_assessment(
        environment=environment,
        findings={
            "summary": summary,
            "exposure_assessment": {},
        },
    )

    return {
        "affected_infrastructure": affected_assets,
        "nearby_infrastructure": nearby_assets,
        "supporting_evidence": supporting_evidence,
        "summary": summary,
        "engineering_assessment": {

            "forecast_rainfall_mm":
                engineering_assessment.forecast_rainfall_mm,
        
            "observed_rainfall_mm":
                engineering_assessment.observed_rainfall_mm,
        
            "rainfall_difference_mm":
                engineering_assessment.rainfall_difference_mm,
        
            "accumulation_24h_mm":
                engineering_assessment.accumulation_24h_mm,
        
            "accumulation_48h_mm":
                engineering_assessment.accumulation_48h_mm,
        
            "accumulation_72h_mm":
                engineering_assessment.accumulation_72h_mm,
        
            "maximum_interval_mm":
                engineering_assessment.maximum_interval_mm,
        
            "precipitation_trend":
                engineering_assessment.precipitation_trend,
        
            "ndwi":
                engineering_assessment.ndwi,
            
            "surface_water_area_m2":
                engineering_assessment.surface_water_area_m2,

            "weather_alerts":
                engineering_assessment.weather_alerts,
        
            "hazard_polygons":
                engineering_assessment.hazard_polygons,
        
            "affected_assets":
                engineering_assessment.affected_assets,
        
            "hospitals":
                engineering_assessment.hospitals,
        
            "schools":
                engineering_assessment.schools,
        
            "fire_stations":
                engineering_assessment.fire_stations,
        
            "police":
                engineering_assessment.police,
        
            "roads":
                engineering_assessment.roads,
        
            "critical_facilities":
                engineering_assessment.exposed_critical_facilities,
        
            "critical_facility_ratio":
                engineering_assessment.exposure_ratio,
        },
    }
