import folium
import streamlit as st
from folium.plugins import (
    MarkerCluster,
    Draw,
    MeasureControl,
)
from streamlit_folium import st_folium
from folium.plugins import Draw
from analysis.environment import StudyArea

def hazard_style(feature):

    return {
        "fillColor": "#60A5FA",
        "color": "#2563EB",
        "weight": 2,
        "fillOpacity": 0.35,
    }

def infrastructure_style(layer):

    styles = {
        "schools": {
            "color": "blue",
            "icon": "graduation-cap",
        },
        "hospitals": {
            "color": "red",
            "icon": "plus-square",
        },
        "fire_stations": {
            "color": "orange",
            "icon": "fire",
        },
        "police": {
            "color": "darkblue",
            "icon": "shield",
        },
        "emergency_services": {
            "color": "darkred",
            "icon": "ambulance",
        },
    }

    return styles.get(
        layer,
        {
            "color": "green",
            "icon": "info-sign",
        },
    )

def waterway_style(feature):

    waterway = (
        feature
        .get("properties", {})
        .get("waterway", "")
        .lower()
    )

    if waterway == "river":

        return {
            "color": "#1D4ED8",
            "weight": 4,
        }

    if waterway == "stream":

        return {
            "color": "#60A5FA",
            "weight": 2,
        }

    return {
        "color": "#3B82F6",
        "weight": 1,
    }

def render_map(
    study_area,
    hazard_gdf,
    infra_gdfs,
    allow_rectangle=False,
    map_instance=0,
):
    
    center_lat, center_lon = study_area.center

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles=None,
    )
    
    folium.TileLayer(
        "OpenStreetMap",
        name="OpenStreetMap",
    ).add_to(m)
    
    folium.TileLayer(
        "CartoDB Dark_Matter",
        name="Dark",
    ).add_to(m)
    
    folium.TileLayer(
        "CartoDB Voyager",
        name="Street",
    ).add_to(m)

    asset_cluster = MarkerCluster(

        disableClusteringAtZoom=15,

        spiderfyOnMaxZoom=True,

        showCoverageOnHover=False,

        zoomToBoundsOnClick=True,
   
        name="Municipal Infrastructure",

    )

    asset_cluster.add_to(m)

    folium.GeoJson(
        study_area.polygon,
        name="Study Area",
        style_function=lambda feature: {

            "fillColor": "#3B82F6",
        
            "fillOpacity": 0.05,
        
            "color": "#60A5FA",
        
            "weight": 3,
        
            "dashArray": "6 4",
        
        },
        highlight_function=lambda feature: {
            "weight": 4,
            "fillOpacity": 0.7,
        },
    ).add_to(m)

    if hazard_gdf is not None and not hazard_gdf.empty:

        folium.GeoJson(
            hazard_gdf,
            name="Flood Assessment",
            style_function=hazard_style,
        ).add_to(m)
    
        minx, miny, maxx, maxy = hazard_gdf.total_bounds
    
        m.fit_bounds(
            [
                [miny, minx],
                [maxy, maxx],
            ]
        )

    if infra_gdfs:

        icons = {
            "schools": "graduation-cap",
            "hospitals": "plus-square",
            "fire_stations": "fire",
            "police": "shield",
            "emergency_services": "ambulance",
            "city_halls": "building",

            "public_works": "wrench",

            "water_treatment": "tint",

            "wastewater_treatment": "recycle",

            "power_substations": "bolt",
        }

        for layer, icon in icons.items():

            gdf = infra_gdfs.get(layer)

            if gdf is None or gdf.empty:
                continue
                
        roads = infra_gdfs.get("primary_roads")

        if roads is not None and not roads.empty:

            folium.GeoJson(
                roads,
                name="Municipal Road Network",
                style_function=lambda feature: {

                    "color": "#4B5563",

                    "weight": 3,

                    "opacity": 0.9,

                },
                tooltip=folium.GeoJsonTooltip(
                    fields=["name"],
                    aliases=["Road"],
                ),
            ).add_to(m)

        waterways = infra_gdfs.get(
            "waterways"
        )
        
        if waterways is not None and not waterways.empty:
        
            folium.GeoJson(
        
                waterways,
        
                name="Hydrography",
        
                style_function=waterway_style,

            ).add_to(m)

        water = infra_gdfs.get(
            "water"
        )

        if water is not None and not water.empty:
        
            folium.GeoJson(
        
                water,
        
                name="Surface Water",
        
                style_function=lambda feature: {
                
                    "fillColor": "#60A5FA",
        
                    "color": "#2563EB",
        
                    "fillOpacity": 0.55,
        
                    "weight": 1,

                },

            ).add_to(m)

    folium.LayerControl().add_to(m)

    if hazard_gdf is None or hazard_gdf.empty:

        minx, miny, maxx, maxy = study_area.bounds

        m.fit_bounds(
            [
                [miny, minx],
                [maxy, maxx],
            ]
        )

    MeasureControl(
        position="bottomleft",
        primary_length_unit="meters",
        secondary_length_unit="kilometers",
    ).add_to(m)

    Draw(
        draw_options={
            "polyline": False,
            "polygon": False,
            "circle": False,
            "marker": False,
            "circlemarker": False,
            "rectangle": allow_rectangle,
        },
        edit_options={
            "edit": allow_rectangle,
            "remove": allow_rectangle,
        },
    ).add_to(m)

    if "map_reset" in st.session_state:

        del st.session_state["map_reset"]
    
    if allow_rectangle:

        st.info(
            "📐 Select the □ Rectangle tool in the upper-right corner of the map, draw your study area, then click **Analyze Custom Area**."
        )

    map_state = st_folium(
        m,
        key=f"municipal_map_{map_instance}",
        width="stretch",
        height=820,
        returned_objects=[
            "last_active_drawing",
            "last_object_clicked",
        ],
    )

    if map_state is None:
        map_state = {}

    st.session_state["map_state"] = map_state

    clicked = map_state.get("last_object_clicked")

    if clicked is not None:
        st.session_state.selected_asset = clicked

    # Return the rectangle as a StudyArea
    drawing = map_state.get("last_active_drawing")

    if allow_rectangle and drawing:

        coords = drawing["geometry"]["coordinates"][0]

        xs = [p[0] for p in coords]
        ys = [p[1] for p in coords]
    
        return StudyArea.from_bbox(
            name="Interactive Study Area",
            west=min(xs),
            south=min(ys),
            east=max(xs),
            north=max(ys),
        )

    return None