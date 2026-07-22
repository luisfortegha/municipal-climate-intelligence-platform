import streamlit as st
import folium
from streamlit_folium import st_folium


def render_gis_preview(
    title,
    study_area,
    layer=None,
    style_function=None,
):

    st.markdown(
        f"""
<div class="card-header">
🗺 {title}
</div>
""",
        unsafe_allow_html=True,
    )

    lat, lon = study_area.center

    m = folium.Map(
        location=[lat, lon],
        zoom_start=11,
        tiles="CartoDB Dark_Matter",
        zoom_control=False,
        control_scale=False,
        dragging=False,
        scrollWheelZoom=False,
    )

    folium.GeoJson(
        study_area.polygon,
        style_function=lambda f: {
            "fillOpacity": 0,
            "color": "#60A5FA",
            "weight": 2,
        },
    ).add_to(m)

    if layer is not None and not layer.empty:

        folium.GeoJson(
            layer,
            style_function=style_function,
        ).add_to(m)

        minx, miny, maxx, maxy = layer.total_bounds

        m.fit_bounds(
            [
                [miny, minx],
                [maxy, maxx],
            ]
        )

    st_folium(
        m,
        height=320,
        width="stretch",
        returned_objects=[],
        key=f"preview_{title}",
    )