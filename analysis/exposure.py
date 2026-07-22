from dataclasses import dataclass

import geopandas as gpd


@dataclass
class ExposureAssessment:

    study_area_km2: float

    hazard_area_km2: float

    percent_area_affected: float

    largest_hazard_polygon_km2: float

    assets_inside: int

    assets_within_100m: int

    assets_within_250m: int

    total_assets: int


def compute_exposure_assessment(

    study_area,

    hazard_gdf: gpd.GeoDataFrame,

    infrastructure: dict,

):

    study = gpd.GeoDataFrame(
        geometry=[study_area.polygon],
        crs="EPSG:4326",
    )
    
    projected_crs = "EPSG:3857"
    
    study = study.to_crs(projected_crs)
    
    study_area_m2 = study.area.iloc[0]
        
    total_assets = 0
    
    for gdf in infrastructure.values():
    
        if gdf is None or gdf.empty:
            continue
    
        total_assets += len(gdf)
    
    if hazard_gdf is None or hazard_gdf.empty:
    
        return ExposureAssessment(
    
            study_area_km2=round(
                study_area_m2 / 1_000_000,
                2,
            ),
    
            hazard_area_km2=0,
    
            percent_area_affected=0,
    
            largest_hazard_polygon_km2=0,
    
            assets_inside=total_assets,
    
            assets_within_100m=0,
    
            assets_within_250m=0,
    
            total_assets=total_assets,
        )
    
    study = gpd.GeoDataFrame(

        geometry=[study_area.polygon],

        crs="EPSG:4326",

    )

    projected_crs = "EPSG:3857"

    study = study.to_crs(projected_crs)

    hazards = hazard_gdf.to_crs(projected_crs)

    study_area_m2 = study.area.iloc[0]

    hazard_union = hazards.union_all()

    hazard_area_m2 = hazard_union.area

    largest_polygon_m2 = hazards.area.max()

    inside = 0

    nearby100 = 0

    nearby250 = 0

    buffer100 = hazard_union.buffer(100)

    buffer250 = hazard_union.buffer(250)

    total_assets = 0

    for gdf in infrastructure.values():

        if gdf.empty:

            continue

        assets = gdf.to_crs(projected_crs)

        total_assets += len(assets)

        for geom in assets.geometry:

            if geom is None:

                continue

            if hazard_union.intersects(geom):

                inside += 1

            elif buffer100.intersects(geom):

                nearby100 += 1

            elif buffer250.intersects(geom):

                nearby250 += 1

    return ExposureAssessment(

        study_area_km2=round(
            study_area_m2 / 1_000_000,
            2,
        ),
    
        hazard_area_km2=round(
            hazard_area_m2 / 1_000_000,
            2,
        ),
    
        percent_area_affected=round(
            hazard_area_m2
            / study_area_m2
            * 100,
            2,
        ),
    
        largest_hazard_polygon_km2=round(
            largest_polygon_m2 / 1_000_000,
            2,
        ),
    
        assets_inside=inside,
    
        assets_within_100m=nearby100,
    
        assets_within_250m=nearby250,
    
        total_assets=total_assets,
    )