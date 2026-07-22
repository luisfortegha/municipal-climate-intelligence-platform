import streamlit as st

from ui.components.earth import render_earth_dashboard
from ui.components.gis_preview import render_gis_preview
from ui.components.map import hazard_style


def render_earth_center(
    study_area,
    gpm,
    environment,
    sentinel,
    terrain,
    hazard_gdf,
    infra_gdfs,
):

    st.markdown(
        """
        <div class="card-header">
        🌎 Earth Observation Center
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------
    # Earth Observation Metrics
    # --------------------------------------------------

    with st.expander(
        "Earth Observation",
        expanded=True,
    ):

        render_earth_dashboard(
            gpm,
            environment,
            sentinel,
            terrain,
        )

    # --------------------------------------------------
    # GIS Preview Cards
    # --------------------------------------------------
    has_surface = (
        environment is not None
        and (
            environment.surface_water_area_m2 or 0
        ) > 0
    )

    has_hazard = (
        hazard_gdf is not None
        and not hazard_gdf.empty
    )

    if has_surface and has_hazard:

        c1, c2 = st.columns(
            [1.2, 1.2],
            gap="large",
        )

        with c1:

            render_gis_preview(
                "Surface Water",
                study_area,
                sentinel.surface_water_gdf,
                lambda feature: {
                    "fillColor": "#2563EB",
                    "color": "#60A5FA",
                    "fillOpacity": 0.55,
                    "weight": 1,
                },
            )

        with c2:

            render_gis_preview(
                "Flood Evidence",
                study_area,
                hazard_gdf,
                hazard_style,
            )

    elif has_surface:

        render_gis_preview(
            "Surface Water",
            study_area,
            sentinel.surface_water_gdf,
            lambda feature: {
                "fillColor": "#2563EB",
                "color": "#60A5FA",
                "fillOpacity": 0.55,
                "weight": 1,
            },
        )

    elif has_hazard:
    
        render_gis_preview(
            "Flood Evidence",
            study_area,
            hazard_gdf,
            hazard_style,
        )

    roads = None

    if infra_gdfs:

        roads = infra_gdfs.get(
            "primary_roads",
        )

    st.write("")

    if roads is not None and not roads.empty:

        render_gis_preview(
            "Road Network",
            study_area,
            roads,
            lambda feature: {
    
                "color": "#F59E0B",
    
                "weight": 2,
    
            },
        )